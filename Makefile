dev:
	docker compose up -d mongo
	python3 -m venv venv
	cp .env.dist .env
	sed -i "" 's/@mongo:/@127.0.0.1:/' .env
