SHELL := /bin/bash

.PHONY: help build run tests migrations migrate dump

DATABASE:= item_menu

help:
	@echo "Использование: make <command>"
	@echo
	@echo "  build              сбилдить приложение"
	@echo "  run                запустить приложение"
	@echo "  tests              запуск тестов (pytest)"
	@echo "  migrations         сделать миграции"
	@echo "  migrate            применить миграции"
	@echo "  dump               снять дамп с БД"

build:
	@pip3 install -r requirements.txt
	@./db/database.sh

run:
	@python3 main.py

tests:
	@pytest tests

migrations:
	@alembic revision -m "auto" --autogenerate --head head
	@git add db/alembic/versions/.

migrate:
	@alembic upgrade head

dump:
	@pg_dump -U postgres $(DATABASE) > $(DATABASE).sql