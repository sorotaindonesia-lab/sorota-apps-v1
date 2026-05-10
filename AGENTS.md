# Sorota Project Memory

This repository is for Sorota, an AI decision assistant for Indonesian UMKM businesses.

## Product Shape

- WhatsApp is the primary customer interface.
- The frontend is an admin dashboard, not the main customer chat surface.
- The backend is the business and AI core.
- The WhatsApp bot is only a channel adapter.
- Neon PostgreSQL is the primary database.
- OpenAI is the primary AI provider.
- Workers handle scheduled/background jobs such as early warning, trend monitoring, research digests, and knowledge processing.
- MCP is planned later, after internal tool boundaries are stable.

## MVP Priorities

Build in this order:

1. Standardize statuses, categories, intents, conversation states, schema, and prompt tasks.
2. Create database migrations.
3. Build the FastAPI backend core.
4. Build the WhatsApp adapter.
5. Add profiling, memory extraction, and simple business assistant skills.
6. Add admin-support APIs.
7. Add Training Center backend.
8. Add Early Warning MVP.
9. Add workers.
10. Add MCP only after internal tools are stable.

Avoid early overbuild: complex multi-agent orchestration, large crawler systems, fine-tuning, MCP-first design, ERP/inventory scope, marketplace integrations, and community features.

## Architecture Rules

- Keep AI calls behind `backend/app/ai/gateway.py`.
- Do not call OpenAI directly from controllers.
- Use deterministic code for arithmetic and business calculations.
- Log AI usage: task type, model, tokens, latency, prompt version, and customer when available.
- Keep WhatsApp logic in `whatsapp-bot/`; keep business decisions in `backend/`.
- Never hardcode secrets. Use environment variables and `.env.example`.

## Core Domain Lists

Customer statuses:

```text
registered
invited
profiling
active
inactive
blocked
invalid
```

Business categories:

```text
kuliner
retail
fashion
laundry
warung
toko_kelontong
coffee_shop
reseller
jasa
lainnya
```

Customer intents:

```text
business_profiling
pricing_advice
margin_calculation
hpp_calculation
supplier_search
market_price_check
competitor_check
product_recommendation
restock_advice
early_warning_explanation
general_business_advice
non_business
```

Conversation states:

```text
NEW
ASK_BUSINESS_NAME
ASK_BUSINESS_CATEGORY
ASK_LOCATION
ASK_MAIN_PRODUCTS
ASK_PRICE_DATA
ACTIVE
```

## Required Backend Endpoints

```text
GET /health
POST /api/customers
GET /api/customers
GET /api/customers/{customer_id}
PATCH /api/customers/{customer_id}
POST /internal/whatsapp/inbound
POST /api/admin-command
GET /api/early-warnings
POST /api/early-warnings/{event_id}/approve
POST /api/early-warnings/{event_id}/send
```

## Implementation Notes

- Backend stack: Python, FastAPI, Pydantic, SQLAlchemy or SQLModel, PostgreSQL driver, OpenAI SDK.
- WhatsApp bot stack: TypeScript preferred.
- Workers stack: Python.
- Frontend is managed manually by the owner. Do not implement full frontend unless asked.
- Use `docs/08-api-contracts.md` as the first API source.
- Use `docs/10-codex-execution-instructions.md` as the first implementation source.

## Completion Report Habit

After execution, report:

- Files changed.
- Important behavior implemented.
- Commands/tests run.
- Anything not run or blocked.
- Suggested next step when useful.
