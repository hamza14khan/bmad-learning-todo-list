.PHONY: up up-build down logs migrate migration test test-be test-fe test-e2e install lint

# ── Dev environment ──────────────────────────────────────────────────────────

up:
	docker compose up

up-build:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f

# ── Database migrations ───────────────────────────────────────────────────────

migrate:
	docker compose exec backend alembic upgrade head

migration:
	@if [ -z "$(msg)" ]; then echo "Usage: make migration msg='your message'"; exit 1; fi
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

# ── Testing ───────────────────────────────────────────────────────────────────

test: test-be

test-be:
	cd backend && pytest --cov --cov-report=term-missing

test-fe:
	cd frontend && npm run test:coverage

test-e2e:
	cd frontend && npx playwright test

# ── Setup ─────────────────────────────────────────────────────────────────────

install:
	cd backend && pip install -r requirements.txt

# ── Code quality ──────────────────────────────────────────────────────────────

lint:
	cd backend && ruff check . && ruff format --check .

lint-fix:
	cd backend && ruff check --fix . && ruff format .
