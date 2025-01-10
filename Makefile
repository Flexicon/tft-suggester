.PHONY: dev api test

dev:
	docker compose up -d mongo
	python3.9 -m venv venv
	. ./venv/bin/activate && pip install -r requirements.txt
	cp .env.dist .env
	sed -i "" 's/@mongo:/@127.0.0.1:/' .env
	@echo "\n--------------------------------------------------------------------\n\nRun: . ./venv/bin/activate\n"

api:
	uvicorn api:app --host=0.0.0.0 --reload

scrape_all:
	python -m scraper

scrape_comps:
	python -m scraper.scrape_comps

scrape_champions:
	python -m scraper.scrape_champions

scrape_items:
	python -m scraper.scrape_items

test:
	python -m pytest
