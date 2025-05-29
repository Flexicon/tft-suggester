.PHONY: dev api test

dev:
	docker compose up -d mongo
	uv venv --python 3.9 .venv
	uv pip install -r requirements.txt
	cp .env.dist .env
	sed -i "" 's/@mongo:/@127.0.0.1:/' .env
	@echo "\n--------------------------------------------------------------------\n\nReady to rock! 🎸\n"

api:
	uv run uvicorn api:app --host=0.0.0.0 --reload

scrape_all:
	uv run python -m scraper

scrape_comps:
	uv run python -m scraper.scrape_comps

scrape_champions:
	uv run python -m scraper.scrape_champions

scrape_items:
	uv run python -m scraper.scrape_items

test:
	uv run python -m pytest -v

test_integration:
	uv run python -m pytest -v -m integration
