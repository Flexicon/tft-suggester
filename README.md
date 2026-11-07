# TFT Suggester Backend

Scrapes Teamfight Tactics data, stores it in MongoDB, and serves it to the companion
SPA through a small FastAPI service.

## Architecture

| Path | Responsibility |
| --- | --- |
| `scraper/` | Collects champions and team comps from [tftactics.gg](https://tftactics.gg), plus items from Community Dragon |
| `cdragon/` | Community Dragon API client (cached item data) |
| `common/models/` | Pydantic models shared by the scrapers and the API |
| `common/db/` | MongoDB connection and collection persistence helpers |
| `api/` | FastAPI app exposing the stored data read-only |
| `tests/` | Unit tests with mocked HTTP, plus Docker-backed integration tests |

Data flow:

```
tftactics.gg / Community Dragon
        │
        ▼
  scraper + Pydantic models
        │
        ▼
  MongoDB (champions, comps, items)
        │
        ▼
  FastAPI  GET /champions  GET /comps  GET /items
```

## Local Development

Requirements:

- Python 3.15+
- Docker 20.10+
- [uv](https://github.com/astral-sh/uv?tab=readme-ov-file#uv)

Prepare the development environment:

```bash
make dev
```

This starts MongoDB, creates `.venv`, installs dependencies, and writes `.env`.

Common commands:

| Command | Description |
| --- | --- |
| `make api` | Run the API at `http://localhost:8000` |
| `make scrape_all` | Run every scraper and trigger the data-fetched webhook |
| `make scrape_champions` | Scrape champions only |
| `make scrape_comps` | Scrape team comps only |
| `make scrape_items` | Scrape items only |
| `make test` | Run unit tests (integration tests are skipped) |
| `make test_integration` | Run Docker-backed integration tests |
| `make format` | Format the codebase with Black |

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `MONGODB_URI` | Yes | MongoDB connection string, e.g. `mongodb://root:pass@127.0.0.1:27017/tft_suggester?authSource=admin` |
| `DATA_FETCHED_WEBHOOK` | No | URL POSTed after a full scrape finishes. The run fails if the webhook returns an error |
| `CORS_SPA_ORIGIN` | No | Allowed SPA origin (defaults to `http://localhost:8080`) |
| `LOG_LEVEL` | No | Python log level for scrapers (defaults to `INFO`) |

## Scrapers

The `worker` GitHub Actions workflow runs every six hours and executes each scraper
in its own job, followed by the webhook.

- **Champions and comps** are scraped from tftactics.gg HTML. The selectors depend on
  the site's markup, so a layout change can break parsing. The fixtures in
  `tests/scraper/mocks/` capture the expected structure.
- **Items** come from the Community Dragon TFT data feed, so they do not depend on
  tftactics markup.
- The comps scraper reuses the champion traits persisted in the `champions`
  collection, so it normally does not re-fetch champion pages. It falls back to
  fetching a champion page when the collection is empty or a champion is missing.
  In CI, the comps job waits for the champions job for this reason.
- Persisting uses a staging collection plus `renameCollection` so readers see either
  the old or the new documents. Deployments that reject `renameCollection` fall back
  to drop-and-insert.
- An empty scrape leaves the existing collection untouched.

## API

| Route | Collection |
| --- | --- |
| `GET /` | Health/hello response |
| `GET /comps` | Team comps, including champions and item recommendations |
| `GET /champions` | Champions with cost and traits |
| `GET /items` | Composite items with their components |

## Tests

```bash
make test              # unit tests, no Docker required
make test_integration  # starts MongoDB with testcontainers
```

Scraper tests use [`responses`](https://github.com/getsentry/responses) to serve the
HTML fixtures from `tests/scraper/mocks/` and assert no live network calls are made.
