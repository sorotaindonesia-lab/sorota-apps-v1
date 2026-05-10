# 10 Codex Execution Instructions

Use this document as implementation instruction for Codex.

## Goal

Implement backend, database migrations, whatsapp-bot, and workers for Sorota MVP. Frontend will be set up manually by owner, but backend APIs must be ready for frontend usage.

## Required root folders

```text
backend/
database-migrations/
frontend/
whatsapp-bot/
workers/
docs/
```

If frontend is empty, create only:

```text
frontend/README.md
```

## Backend implementation requirements

Use:

```text
Python
FastAPI
Pydantic
SQLAlchemy or SQLModel
psycopg/postgres driver
OpenAI SDK
```

Create structure:

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── ai/
│   ├── calculators/
│   └── main.py
├── tests/
├── requirements.txt
└── .env.example
```

Must include endpoints:

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

## Database migrations

Create SQL files in:

```text
database-migrations/
```

Suggested files:

```text
001_extensions.sql
002_admins_customers_businesses.sql
003_products_messages_sessions.sql
004_memories_recommendations_usage.sql
005_training_knowledge_rules_skills.sql
006_early_warnings.sql
007_indexes.sql
```

## WhatsApp bot implementation requirements

Use Node.js/TypeScript or Python. Prefer TypeScript for adapter.

Create structure:

```text
whatsapp-bot/
├── src/
│   ├── index.ts
│   ├── config.ts
│   ├── webhook.ts
│   ├── whatsapp-client.ts
│   └── backend-client.ts
├── package.json
├── tsconfig.json
└── .env.example
```

Responsibilities:

- Verify webhook challenge.
- Receive inbound messages.
- Forward inbound message to backend.
- Send backend reply to WhatsApp.
- Send template welcome message when requested.

## Workers implementation requirements

Use Python.

Create structure:

```text
workers/
├── app/
│   ├── early_warning_worker.py
│   ├── scheduler.py
│   ├── db.py
│   └── services/
├── requirements.txt
└── .env.example
```

MVP worker:

- Load active early_warning_rules.
- Generate draft warning events with placeholder logic.
- Respect rate limit.
- Do not auto-send unless ENABLE_EARLY_WARNING_AUTO_SEND=true.

## AI requirements

All OpenAI calls through:

```text
backend/app/ai/gateway.py
```

Create prompt files:

```text
backend/app/ai/prompts/intent_router.md
backend/app/ai/prompts/business_profiler.md
backend/app/ai/prompts/memory_extractor.md
backend/app/ai/prompts/answer_composer.md
backend/app/ai/prompts/admin_query_parser.md
backend/app/ai/prompts/early_warning_composer.md
```

Every AI call must log:

```text
task_type
model
input_tokens
output_tokens
latency_ms
prompt_version
customer_id optional
```

## Calculators

Implement deterministic calculators:

```text
calculate_margin(selling_price, hpp)
recommend_price(hpp, target_margin_percent)
```

Do not use AI for arithmetic.

## Frontend note

Do not implement full frontend unless asked. Create:

```text
frontend/README.md
```

Include API pages needed:

```text
Customer List
Add Customer
Customer Detail
Training Center
Early Warning Review
Usage Dashboard
Admin Command Center
```

## Quality requirements

- Use environment variables only.
- Never hardcode secrets.
- Provide `.env.example`.
- Validate input with Pydantic/Zod.
- Use clear service boundaries.
- Keep whatsapp-bot as adapter only.
- Keep AI logic in backend.

