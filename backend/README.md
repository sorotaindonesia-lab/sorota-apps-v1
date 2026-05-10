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
