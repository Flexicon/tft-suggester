dev:
	docker compose up -d mongo
	python3.9 -m venv venv
	. ./venv/bin/activate && pip install -r requirements.txt
	cp .env.dist .env
	sed -i "" 's/@mongo:/@127.0.0.1:/' .env
	@echo "\n--------------------------------------------------------------------\n\nRun: . ./venv/bin/activate\n"

test:
	python -m pytest
