# Sorota Backend

FastAPI backend for the Sorota MVP.

## Local Run

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Database Migrations

This backend uses SQLAlchemy ORM models plus Alembic migrations.

Set `DATABASE_URL` in `backend/.env` first:

```text
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require
```

`postgresql://...` also works; the app normalizes it to `postgresql+psycopg://...` so SQLAlchemy uses the installed `psycopg` v3 driver.

Run the latest migration:

```powershell
cd backend
python -m pip install -r requirements.txt
.\.venv\Scripts\alembic.exe upgrade head
```

Create a new ORM-driven migration after changing models:

```powershell
cd backend
.\.venv\Scripts\alembic.exe revision --autogenerate -m "describe change"
.\.venv\Scripts\alembic.exe upgrade head
```

The older SQL files in `../database-migrations/` are kept as a readable schema reference. For app development, prefer Alembic.

## Important Endpoints

```text
GET /health
POST /api/customers
GET /api/customers
GET /api/customers/{customer_id}
PATCH /api/customers/{customer_id}
POST /internal/whatsapp/inbound
POST /internal/telegram/inbound
POST /api/admin-command
GET /api/early-warnings
POST /api/early-warnings/{event_id}/approve
POST /api/early-warnings/{event_id}/send
```

## Active Assistant MVP

After customer profiling reaches `ACTIVE`, the backend uses structured context plus deterministic calculators before composing a final answer. If `OPENAI_API_KEY` is configured, calculator results are passed through the answer composer for a more natural response. If not, a local natural fallback is used.

Margin example:

```text
harga jual 18000 hpp 11500 margin berapa?
```

The reply includes selling price, HPP, margin amount, margin percent, and a practical recommendation.

Recommend price example:

```text
hpp 11500 target margin 30 harga jual berapa?
```

The reply includes HPP, target margin, minimum price, and a rounded selling price range.

For non-calculator business questions, active customers still get a mentor-style business response using their profile context:

```text
jualan saya sepi, harus gimana?
mau bikin promo bundling
stok saya mulai habis
cara cari supplier murah
```

Active chat also extracts database-ready business facts from natural messages and saves them into existing ORM tables when the user gives useful data:

```text
Saya jual ayam geprek di Bandung, harga jualnya 18 ribu, HPP sekitar 11.500.
```

That message can update the business category/location, product selling price/HPP/margin, and `main_product` memory. No new migration is required for this mapping layer because it uses the existing `businesses`, `products`, and `user_memories` tables.

OpenAI-compatible API providers can be configured with:

```text
OPENAI_API_KEY=your_key
OPENAI_BASE_URL=https://your-openai-compatible-base-url/v1
```

## Troubleshooting

If you see this error:

```text
ModuleNotFoundError: No module named 'psycopg2'
```

Make sure the latest code is pulled and dependencies are installed:

```powershell
cd backend
pip install -r requirements.txt
```

The backend uses `psycopg` v3, not `psycopg2`.

If you see this error while running Alembic:

```text
ModuleNotFoundError: No module named 'psycopg'
```

PowerShell may be using a global `alembic.exe` instead of the virtualenv. Run Alembic through the active Python:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\.venv\Scripts\alembic.exe upgrade head
```
