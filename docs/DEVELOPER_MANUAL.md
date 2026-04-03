# Wealth OS — Developer Manual

## Table of Contents
1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Local Setup](#local-setup)
5. [Environment Variables](#environment-variables)
6. [Database](#database)
7. [Backend Architecture](#backend-architecture)
8. [API Reference](#api-reference)
9. [Parser Framework](#parser-framework)
10. [Calculators](#calculators)
11. [Frontend Architecture](#frontend-architecture)
12. [Running Tests](#running-tests)
13. [Adding a New Parser](#adding-a-new-parser)
14. [Adding a New API Endpoint](#adding-a-new-api-endpoint)
15. [Deployment](#deployment)

---

## Overview

Wealth OS is a full-stack personal wealth management system designed for Saudi and international investors. It tracks brokerage holdings, private deals, and provides portfolio analytics with a focus on local Saudi platforms.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI 0.111, Python 3.11 |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Charts | Recharts |
| Containerization | Docker + Docker Compose |
| Financial math | scipy (XIRR via Newton-Raphson) |
| Data parsing | pandas, openpyxl |

---

## Project Structure

```
BS-Wealth-System/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # Route handlers (9 routers)
│   │   │   ├── auth.py
│   │   │   ├── platforms.py
│   │   │   ├── accounts.py
│   │   │   ├── assets.py
│   │   │   ├── deals.py
│   │   │   ├── transactions.py
│   │   │   ├── cashflows.py
│   │   │   ├── imports.py
│   │   │   └── analytics.py
│   │   ├── calculators/     # Financial calculation engines
│   │   │   ├── brokerage_calc.py   # FIFO P&L
│   │   │   ├── deal_calc.py        # XIRR
│   │   │   └── portfolio_calc.py   # Aggregation
│   │   ├── core/            # Config, security, logging
│   │   ├── db/              # Base, models registry, session
│   │   ├── models/          # SQLAlchemy ORM models (11 models)
│   │   ├── parsers/         # CSV/XLSX import parsers (13)
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── scripts/         # seed.py
│   │   └── services/        # market_data, insights
│   ├── alembic/             # Database migrations
│   ├── tests/               # pytest test suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js App Router pages
│   │   │   ├── login/
│   │   │   ├── overview/
│   │   │   ├── investments/
│   │   │   ├── insights/
│   │   │   └── imports/
│   │   ├── components/      # Reusable UI components
│   │   │   ├── charts/
│   │   │   ├── layout/
│   │   │   └── ui/
│   │   ├── lib/             # API client, utilities
│   │   └── types/           # TypeScript interfaces
│   ├── Dockerfile
│   └── package.json
├── templates/               # CSV import templates
├── infra/                   # GCP and Azure deployment notes
├── docker-compose.yml
└── .env.example
```

---

## Local Setup

### Prerequisites
- Docker Desktop (Mac/Windows/Linux)
- Git
- VS Code (recommended)

### Steps

1. `git clone https://github.com/Sarah906/BS-Wealth-System.git` — clone the repo
2. `cd BS-Wealth-System` — enter the project folder
3. `cp .env.example .env` — create your local environment file
4. `docker compose up --build` — build and start all services

### Access Points
| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

### Demo Login
- **Username:** `demo`
- **Password:** `Demo@1234`

---

## Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `wealthos` | Database name |
| `POSTGRES_USER` | `wealthos` | Database user |
| `POSTGRES_PASSWORD` | `wealthos_secret` | Database password |
| `SECRET_KEY` | `change_me_in_production_32chars_min` | JWT signing key — **change in production** |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Token lifetime (24 hours) |
| `ENVIRONMENT` | `development` | `development` or `production` |
| `LOG_LEVEL` | `INFO` | Logging level |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed frontend origins |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend URL used by frontend |

---

## Database

### Models (11 tables)

| Model | Table | Description |
|-------|-------|-------------|
| `User` | `users` | Authentication and profile |
| `Platform` | `platforms` | Brokers and investment platforms |
| `Account` | `accounts` | User accounts per platform |
| `Asset` | `assets` | Stocks, sukuk, funds, etc. |
| `Deal` | `deals` | Private equity / deal investments |
| `Transaction` | `transactions` | Buy/sell/dividend/fee records |
| `DealCashflow` | `deal_cashflows` | Capital calls and distributions |
| `PriceHistory` | `price_history` | Daily closing prices |
| `FXRate` | `fx_rates` | Currency exchange rates |
| `RawImport` | `raw_imports` | Import job records |
| `ImportMapping` | `import_mappings` | Column mapping configs per platform |

### Migrations

```bash
# Apply all migrations
docker compose exec backend alembic upgrade head

# Create a new migration after model changes
docker compose exec backend alembic revision --autogenerate -m "description"

# Roll back one step
docker compose exec backend alembic downgrade -1
```

### Seed Data

The seed script runs automatically on startup. To re-run manually:

```bash
docker compose exec backend python -m app.scripts.seed
```

Seed creates:
- 11 Saudi platforms (Derayah, Al Rajhi, Alinma, etc.)
- 1 demo user (`demo` / `Demo@1234`)
- 8 sample deals
- Brokerage transactions with 5-year mock price history

---

## Backend Architecture

### Request Flow

```
HTTP Request
    → FastAPI router (api/v1/*.py)
    → Pydantic schema validation
    → Business logic / calculator
    → SQLAlchemy ORM
    → PostgreSQL
    → Pydantic response schema
    → JSON response
```

### Authentication

JWT bearer tokens. Every protected endpoint uses the `get_current_user` dependency from `api/deps.py`.

```python
# Example protected endpoint
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    ...
```

Token flow:
1. `POST /api/v1/auth/login` → returns `access_token`
2. Include in header: `Authorization: Bearer <token>`

### Adding Dependencies

```python
# api/deps.py provides:
get_db()          # SQLAlchemy session
get_current_user() # Authenticated user from JWT
```

---

## API Reference

Base URL: `http://localhost:8000/api/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/login` | Get JWT token |
| POST | `/auth/register` | Create account |
| GET | `/platforms` | List all platforms |
| GET/POST | `/accounts` | User accounts |
| GET/POST | `/assets` | Assets |
| GET/POST | `/deals` | Private deals |
| GET/POST | `/transactions` | Brokerage transactions |
| GET/POST | `/cashflows` | Deal cashflows |
| POST | `/imports/upload` | Upload CSV/XLSX file |
| POST | `/imports/run` | Execute import |
| GET | `/imports/history` | Import history |
| GET | `/analytics/overview` | Portfolio summary |
| GET | `/analytics/allocation` | Allocation breakdown |
| GET | `/analytics/cashflows` | Monthly cashflow chart data |
| GET | `/analytics/insights` | Risk alerts |

Full interactive docs at `http://localhost:8000/docs`.

---

## Parser Framework

### Architecture

```
parsers/
├── base.py               # BaseParser (abstract)
├── brokerage_base.py     # BrokerageParser extends BaseParser
├── deal_base.py          # DealParser extends BaseParser
└── generic_parsers.py    # All platform-specific parsers
```

### How Parsers Work

1. User uploads a CSV/XLSX file
2. System detects the platform and selects the correct parser
3. Parser reads the file using pandas
4. Rows are normalized into `Transaction` or `DealCashflow` objects
5. Records are saved to the database

### Implemented Parsers

| Parser Class | Platform | Type |
|-------------|----------|------|
| `DerayahParser` | Derayah | Brokerage |
| `AlRajhiParser` | Al Rajhi Capital | Brokerage |
| `AlinmaParser` | Alinma Invest | Brokerage |
| `TamraParser` | Tamra | Deals |
| `AseelParser` | Aseel | Deals |
| `SukukParser` | Generic Sukuk | Deals |
| `ManafaParser` | Manafa | Deals |
| `SafqahParser` | Safqah | Deals |
| `TarmeezParser` | Tarmeez | Brokerage |
| `AwaedParser` | Awaed | Deals |
| `DerayahSmartParser` | Derayah (smart) | Brokerage |

---

## Calculators

### Brokerage Calculator (`brokerage_calc.py`)

Uses **FIFO** (First In, First Out) cost basis method.

Outputs per asset:
- `realized_pnl` — profit/loss from sold positions
- `unrealized_pnl` — current open position gain/loss
- `total_fees` — commissions and charges
- `dividend_income` — total dividends received
- `win_rate` — percentage of profitable trades
- `expectancy` — average expected gain per trade

### Deal Calculator (`deal_calc.py`)

Uses **XIRR** (Extended Internal Rate of Return) via Newton-Raphson iteration.

Outputs per deal:
- `invested_capital` — total capital calls
- `distributed_capital` — total distributions received
- `nav` — current net asset value
- `roi` — return on investment (%)
- `xirr` — annualized return rate (%)
- `moic` — multiple on invested capital

### Portfolio Calculator (`portfolio_calc.py`)

Aggregates across all accounts and asset types:
- Allocation by platform, asset type, currency
- Monthly cashflow timeline
- Total portfolio value

---

## Frontend Architecture

### Pages

| Route | Page | Description |
|-------|------|-------------|
| `/login` | Login | JWT authentication |
| `/overview` | Overview Dashboard | Portfolio summary, allocation charts, cashflow bar chart |
| `/investments` | Investments | Brokerage table + deals table with tabs |
| `/insights` | Insights | Risk alerts by severity |
| `/imports` | Imports | File upload, parser selection, import history |

### Key Files

| File | Purpose |
|------|---------|
| `src/lib/api.ts` | Axios API client with JWT interceptor |
| `src/lib/utils.ts` | Formatting helpers (currency, %, dates) |
| `src/types/index.ts` | TypeScript interfaces for all API types |
| `src/components/layout/AppLayout.tsx` | Shell with sidebar |
| `src/components/charts/AllocationPie.tsx` | Recharts pie chart |
| `src/components/charts/CashflowBar.tsx` | Recharts bar chart |

### API Client

```typescript
// src/lib/api.ts
import api from '@/lib/api';

// GET request
const data = await api.get('/analytics/overview');

// POST request
const result = await api.post('/auth/login', { username, password });
```

The client automatically attaches the JWT token from `localStorage`.

---

## Running Tests

```bash
# Run all tests
docker compose exec backend pytest

# Run with verbose output
docker compose exec backend pytest -v

# Run a specific test file
docker compose exec backend pytest tests/test_brokerage_calc.py

# Run with coverage
docker compose exec backend pytest --cov=app
```

### Test Files

| File | Tests |
|------|-------|
| `tests/test_brokerage_calc.py` | 7 tests — FIFO calculator |
| `tests/test_deal_calc.py` | 7 tests — XIRR calculator |

---

## Adding a New Parser

1. **Open** `backend/app/parsers/generic_parsers.py`

2. **Add a new class** extending `BrokerageParser` or `DealParser`:

```python
class MyBrokerParser(BrokerageParser):
    platform_name = "My Broker"

    def parse(self, file_path: str) -> list[dict]:
        df = pd.read_csv(file_path)
        transactions = []
        for _, row in df.iterrows():
            transactions.append({
                "trade_date": row["Date"],
                "transaction_type": "BUY",
                "asset_symbol": row["Symbol"],
                "quantity": float(row["Qty"]),
                "price": float(row["Price"]),
                "fees": float(row["Commission"]),
                "currency": "SAR",
            })
        return transactions
```

3. **Register the parser** in `backend/app/api/v1/imports.py` — add it to the parser registry dict.

4. **Add a CSV template** to `templates/` so users know the expected format.

---

## Adding a New API Endpoint

1. **Create or open** a router file in `backend/app/api/v1/`

2. **Add your route:**

```python
@router.get("/my-endpoint", response_model=MySchema)
def my_endpoint(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = db.query(MyModel).filter(MyModel.user_id == current_user.id).all()
    return result
```

3. **Register the router** in `backend/app/api/v1/router.py`:

```python
from app.api.v1 import my_module
api_router.include_router(my_module.router, prefix="/my-prefix", tags=["my-tag"])
```

4. **Add a Pydantic schema** in `backend/app/schemas/` for request/response validation.

---

## Deployment

### GCP (Cloud Run)

See `infra/gcp/notes.md` for full steps. High-level:

1. Push images to Google Artifact Registry
2. Deploy backend to Cloud Run
3. Deploy frontend to Cloud Run
4. Use Cloud SQL for PostgreSQL
5. Set environment variables via Secret Manager

### Azure (App Service)

See `infra/azure/notes.md` for full steps. High-level:

1. Push images to Azure Container Registry
2. Deploy via Azure App Service (containers)
3. Use Azure Database for PostgreSQL
4. Configure environment variables in App Service settings

### Production Checklist

- [ ] Change `SECRET_KEY` to a random 32+ character string
- [ ] Set `ENVIRONMENT=production`
- [ ] Set strong `POSTGRES_PASSWORD`
- [ ] Set `CORS_ORIGINS` to your actual frontend domain
- [ ] Enable HTTPS (handled by Cloud Run / App Service automatically)
- [ ] Set up database backups
