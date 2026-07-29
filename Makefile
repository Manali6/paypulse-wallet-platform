# Wallet Platform — Makefile
# ==============================================================================

.PHONY: up down logs test migrate seed lint clean

# --- Docker Compose ---
up:
	cp -n .env.example .env 2>/dev/null || true
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f

logs-backend:
	docker compose logs -f backend

# --- Database ---
migrate:
	docker compose exec backend alembic upgrade head

migration:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

seed:
	docker compose exec backend python -m app.seed

# --- Testing ---
test:
	docker compose exec backend pytest tests/ -v --cov=app --cov-report=term-missing

test-unit:
	docker compose exec backend pytest tests/unit/ -v

test-integration:
	docker compose exec backend pytest tests/integration/ -v

# --- Linting ---
lint:
	docker compose exec backend ruff check app/ tests/
	docker compose exec backend ruff format --check app/ tests/

lint-fix:
	docker compose exec backend ruff check --fix app/ tests/
	docker compose exec backend ruff format app/ tests/

# --- Utilities ---
shell:
	docker compose exec backend bash

psql:
	docker compose exec postgres psql -U wallet -d wallet_db

redis-cli:
	docker compose exec redis redis-cli

clean:
	docker compose down -v --rmi local
	rm -rf backend/__pycache__ backend/app/__pycache__

# --- Health ---
health:
	curl -s http://localhost:8000/health | python3 -m json.tool
