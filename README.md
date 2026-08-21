<div align="center">

# PortfolioTracker

**Self-hosted investment portfolio tracker for Indian investors.**

Track NSE/BSE investments, transactions, dividends, interest, savings, property, payroll, and tax summaries in one private English-first application.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/rosh2525/PortfolioTracker/ci.yml?label=CI&logo=github)](https://github.com/rosh2525/PortfolioTracker/actions/workflows/ci.yml)
[![Django](https://img.shields.io/badge/Django-6-092E20?logo=django)](https://www.djangoproject.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16-000000?logo=nextdotjs)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)](https://www.docker.com/)

</div>

## Features

- Portfolio management for stocks, ETFs, funds, and crypto, with Yahoo Finance pricing and NSE/BSE symbol support.
- FIFO, LIFO, and weighted-average cost engines; position value, cost basis, and unrealized P&L.
- Buy, sell, and gift transactions with commissions and taxes; CSV exports and import deduplication.
- Dividend and interest tracking with withholding/TDS, fees, net income, and yearly summaries.
- Multiple account types, balance snapshots, bulk balance updates, and scheduled portfolio snapshots.
- Net-worth, portfolio-evolution, monthly/annual savings, and savings-goal analytics.
- Property and mortgage tracking with interactive amortization events, schedules, charts, and comparisons.
- Payroll and employer tracking, including optional payslip-assisted entry and soft reconciliation warnings.
- Country-neutral tax analysis, with India as the default residence and an explicit notice that India-specific filing automation is not yet available.
- JSON backup/restore, retention controls, storage monitoring, privacy masking, Google OAuth, JWT cookies, rate limiting, and strict per-user isolation.
- English-only interface, Indian number formatting, and INR defaults.
- Responsive desktop/mobile UI and a backend-free demo mode.

## Quick start

```bash
git clone https://github.com/rosh2525/PortfolioTracker.git
cd PortfolioTracker
cp .env.example .env
docker compose up --build
```

| Service | URL |
|---|---|
| Application | `http://localhost:3000` |
| API | `http://localhost:8000/api/` |
| Swagger UI | `http://localhost:8000/api/schema/swagger-ui/` |
| Django Admin | `http://localhost:8000/admin/` |

Before production use, copy `.env.production.example` to `.env` and replace every `CHANGE_ME` value. Production images are published to GitHub Container Registry when a `v*` tag is pushed.

## Technology

PortfolioTracker uses Next.js, React, TypeScript, Django REST Framework, PostgreSQL, Redis, Celery, Nginx, and Docker Compose. Browser API calls use a Next.js backend-for-frontend proxy, keeping JWTs in HTTP-only cookies.

## Development

See [development setup](docs/DEVELOPMENT.md), [contributing guidelines](docs/CONTRIBUTING.md), [architecture](docs/architecture.md), and [security policy](docs/SECURITY.md).

## License

[MIT](LICENSE) © 2026 rosh2525
