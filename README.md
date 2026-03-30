# Wealth OS

A production-quality personal wealth management system for consolidating investments across Saudi platforms (Derayah, Alinma, Al Rajhi, Aseel, Derayah Smart, Tamra, Awaed, Sukuk, Tarmeez, Safqah, Manafa) and future US brokerage accounts.

## What It Does

- **Single source of truth** for all investments from 2019 to today
- **Brokerage tracking**: buy/sell/dividend transactions with FIFO P&L, win/loss stats
- **Deal-based tracking**: investments, distributions, redemptions with IRR/XIRR calculations
- **Portfolio analytics**: allocation by platform, asset type, currency; monthly cashflows
- **Rules-based insights**: concentration risk, stale deals, upcoming maturities, missing data
- **Data import**: CSV/Excel upload with per-platform parsers and preview before commit
- **Market data abstraction**: pluggable price and FX providers (mock included for development)

---

## Architecture

```
backend/          FastAPI + SQLAlchemy 2.x + Alembic + PostgreSQL
frontend/         Next.js 14 + TypeScript + Tailwind + Recharts
infra/            Cloud deployment notes (GCP + Azure)
templates/        Standard CSV import templates
docker-compose.yml
```

### Platform categories handled

| Category | Platforms |
|---|---|
| Brokerage | Derayah, Alinma, Al Rajhi |
| Robo/Managed | Aseel, Derayah Smart |
| Sukuk/Fixed Income | Sukuk, Awaed |
| Deal/Crowdfunding | Tamra, Tarmeez, Safqah, Manafa |

---

## Quick Start (Local Dev with Docker)

### Prerequisites
- Docker Desktop (Apple Silicon / M1 compatible)
- git

### 1. Clone and configure environment

```bash
git clone <repo>
cd BS-Wealth-System
cp .env.example .env
# Defaults work for local dev — edit passwords if needed
```

### 2. Run everything

```bash
docker compose up --build
```

This will:
- Start PostgreSQL
- Run Alembic migrations automatically
- Run the seed script (platforms + demo data)
- Start FastAPI backend on port 8000
- Start Next.js frontend on port 3000

### 3. Open the app

- **Frontend**: http://localhost:3000
- **API docs**: http://localhost:8000/docs
- **Login**: username `demo` / password `Demo@1234`

---

## Environment Variables

Copy `.env.example` to `.env`:

| Variable | Description | Default |
|---|---|---|
| `POSTGRES_DB` | Database name | `wealthos` |
| `POSTGRES_USER` | DB user | `wealthos` |
| `POSTGRES_PASSWORD` | DB password | `wealthos_secret` |
| `SECRET_KEY` | JWT signing key — **change in production** | `change_me...` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL | `1440` (24h) |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |
| `NEXT_PUBLIC_API_URL` | Backend URL visible to browser | `http://localhost:8000` |
| `SAUDI_MARKET_API_KEY` | Saudi market data provider (future) | empty |
| `US_MARKET_API_KEY` | US market data provider (future) | empty |
| `FX_PROVIDER_API_KEY` | FX rate provider (future) | empty |

---

## Running Migrations

```bash
cd backend
alembic upgrade head

# After model changes:
alembic revision --autogenerate -m "describe_change"
```

---

## Running the Seed Script

Runs automatically on `docker compose up`. Manual run:

```bash
cd backend
python -m app.scripts.seed
```

Inserts: all 11 Saudi platforms, demo user, sample Saudi stocks, Derayah brokerage transactions, 8 deals across all deal-based platforms, 5 years of mock price history.

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

14 tests covering FIFO brokerage calc, deal/IRR calc, edge cases.

---

## Import Workflow

1. Download a template from `templates/` (or the Imports page)
2. Fill in your transactions or deal cashflows
3. Go to **Imports** in the app
4. Select platform + parser, upload the file
5. Click **Preview** to verify parsed rows
6. Click **Run Import** to write to database

### Parser selection

| Data | Parser |
|---|---|
| Any brokerage CSV (standard format) | `generic_brokerage` |
| Any deal/fund CSV (standard format) | `generic_deal` |
| Derayah | `derayah` |
| Al Rajhi | `alrajhi` |
| Alinma | `alinma` |
| Tamra | `tamra` |
| Aseel | `aseel` |
| Sukuk | `sukuk` |
| Manafa | `manafa` |
| Safqah | `safqah` |
| Tarmeez | `tarmeez` |
| Awaed | `awaed` |
| Derayah Smart | `derayah_smart` |

> Platform-specific parsers are scaffolded. Adjust `column_map` in `backend/app/parsers/generic_parsers.py` once you have real export samples from each platform.

---

## Adding Real Market Data Providers

Edit `backend/app/services/market_data_service.py`:

```python
class MySaudiProvider(PriceProvider):
    def get_latest_price(self, symbol: str) -> Optional[float]:
        # call your API
        ...

# In MarketDataService.__init__:
self._saudi_price_provider = MySaudiProvider()
```

---

## Adding a New Platform Parser

```python
# backend/app/parsers/generic_parsers.py
class MyPlatformParser(BrokerageParserBase):
    name = "myplatform"
    column_map = {
        "date": "Trade Date",
        "symbol": "Symbol",
        ...
    }
```

Then register in `backend/app/parsers/__init__.py`.

---

## Cloud Deployment

- `infra/gcp/notes.md` — Google Cloud Run / Compute Engine
- `infra/azure/notes.md` — Azure App Service / Container Instances

All config is env-var driven. PostgreSQL can move to managed Cloud SQL or Azure Database with only a `DATABASE_URL` change.

---

## Calculation Details

**Brokerage (FIFO)**
- Each BUY creates a cost lot including proportional fees
- SELLs consume oldest lots first
- Realized P&L per trade, plus unrealized P&L vs current price
- Win/loss rate, avg gain/loss, expectancy over all closed trades

**Deal-based (XIRR)**
- INVESTMENT = capital outflow (negative in XIRR)
- DISTRIBUTION + REDEMPTION = cash back (positive in XIRR)
- VALUATION = latest NAV snapshot (terminal value for active deals)
- IRR uses Newton-Raphson convergence
- Simple ROI = (returned + current value - invested - fees) / invested

---

## Project Structure

```
backend/app/
  api/v1/         auth, platforms, accounts, assets, deals,
                  transactions, cashflows, imports, analytics
  calculators/    brokerage_calc.py, deal_calc.py, portfolio_calc.py
  core/           config.py, security.py, logging.py
  db/             session.py, base.py
  jobs/           price_sync.py
  models/         user, platform, account, asset, deal, transaction,
                  cashflow, price, fx_rate, import_record (11 tables)
  parsers/        base, brokerage_base, deal_base, generic_parsers (13 parsers)
  repositories/   base, user_repo, transaction_repo
  schemas/        user, platform, account, asset, deal, transaction,
                  cashflow, analytics
  scripts/        seed.py
  services/       market_data_service.py, insights_service.py

frontend/src/
  app/            login/, overview/, investments/, insights/, imports/
  components/     layout/ (Sidebar, AppLayout)
                  ui/ (StatCard, LoadingSpinner, EmptyState)
                  charts/ (AllocationPie, CashflowBar)
  lib/            api.ts, utils.ts
  types/          index.ts
```
