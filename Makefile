.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

install: ## Установить зависимости
	uv sync

env: ## Создать .env.local из шаблона (права 600)
	@test -f .env.local && echo ".env.local уже есть" || (cp .env.example .env.local && chmod 600 .env.local && echo "создан .env.local")

login: ## Войти в Telegram и сохранить сессию в .env.local
	uv run python -m app.cli login

doctor: ## Проверить ключи, сессию и настройки доступа
	uv run python -m app.cli doctor

register: ## Подключить сервер к Claude Code для текущего пользователя
	claude mcp add -s user murzins-telegram -- uv --directory $(CURDIR) run murzins-telegram-mcp

hooks: ## Поставить pre-commit хуки (в т.ч. проверку на секреты)
	uv run pre-commit install

lint: ## Проверить стиль
	uv run ruff check app settings tests
	uv run ruff format --check app settings tests

types: ## Проверить типы
	uv run mypy

test: ## Прогнать тесты
	uv run pytest

check: lint types test ## Полная проверка

fmt: ## Отформатировать код
	uv run ruff format app settings tests
	uv run ruff check --fix app settings tests

.PHONY: help install env login doctor register hooks lint types test check fmt
