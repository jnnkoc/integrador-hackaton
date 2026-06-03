.PHONY: up down logs migrate shell restart build test

up:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up -d --build

down:
	docker compose down

logs:
	docker compose logs -f api

migrate:
	docker compose exec api python -c "from database import engine; from models import Base; Base.metadata.create_all(engine); print('Tables created.')"

shell:
	docker compose exec api bash

restart: down up

build:
	docker compose build

test:
	pytest tests/ -v
