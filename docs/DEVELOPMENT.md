# Development

## Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

## Frontend

PortfolioTracker requires the Node.js version in `.nvmrc`.

```bash
cd frontend
npm ci
npm run dev
```

Use `NEXT_PUBLIC_DEMO_MODE=true npm run dev` to expose the backend-free demo login.

## Backend

Use Python 3.12 with PostgreSQL and Redis available through the values in `.env`.

```bash
cd backend
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/pytest
```

## Required checks

```bash
cd backend && .venv/bin/ruff check . && .venv/bin/ruff format --check .
cd frontend && npm test && npx tsc --noEmit && npm run lint && npm run build
```
