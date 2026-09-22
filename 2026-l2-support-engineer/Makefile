.PHONY: dev test build
dev:
	uv run --python 3.12 --no-project scripts/dev.py

frontend/node_modules/.package-lock.json: frontend/package-lock.json frontend/package.json
	cd frontend && npm ci --no-audit --no-fund

test: frontend/node_modules/.package-lock.json
	cd backend && uv sync --frozen && uv run --frozen pytest
	cd frontend && npm test

build: frontend/node_modules/.package-lock.json
	cd frontend && npm run build
