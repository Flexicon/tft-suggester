# TFT Suggester Backend

## Local Development

Requirements:

- Python 3.9.7+
- Docker 20.10+

To prepare the development environment,
run the following in your terminal (only tested on macOS):

```bash
make dev && . ./venv/bin/activate
```

To run...

- the api server: `$ uvicorn api:app --host=0.0.0.0 --reload`
- the web scrapers: `$ python -m scraper`
