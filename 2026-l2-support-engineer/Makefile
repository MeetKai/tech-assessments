.PHONY: dev test build
dev:
	uv run --python 3.12 --no-project scripts/dev.py

test:
	cd backend && uv sync --frozen && uv run --frozen pytest
	cd frontend && npm ci --no-audit --no-fund && npm test

build:
	cd frontend && npm ci --no-audit --no-fund && npm run build
