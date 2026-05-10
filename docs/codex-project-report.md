# Codex Project Report

Generated from the current `docs/` folder on 2026-05-10.

## Executive Summary

Sorota is an AI decision assistant for Indonesian UMKM businesses. The customer-facing channel is WhatsApp, while the frontend is an admin dashboard. The main product is not a chat UI; it is a business decision engine that uses customer business memory, structured data, market/knowledge inputs, deterministic calculators, and OpenAI-powered reasoning.

The MVP should focus on customer registration, WhatsApp onboarding, business profiling, customer/business data persistence, simple margin and pricing advice, admin visibility, AI usage logging, and an early-warning draft/approval workflow.

## Main Runtime Responsibilities

Backend:

- Owns business logic, AI orchestration, customer/business APIs, memory extraction, answer composition, usage logging, and early-warning APIs.
- Must expose clear contracts for the admin dashboard, WhatsApp bot, and workers.
- Must route all OpenAI usage through `backend/app/ai/gateway.py`.

WhatsApp bot:

- Verifies webhooks.
- Receives inbound WhatsApp messages.
- Sends approved templates and normal messages.
- Forwards inbound messages to the backend.
- Does not perform core AI reasoning, pricing calculations, or complex database work.

Workers:

- Run early-warning scans, trend/research jobs, market crawling placeholders, knowledge refresh, and scheduled customer insight tasks.
- MVP starts with draft warning generation and admin approval mode.

Frontend:

- Managed manually by the owner.
- Backend must support dashboard pages such as customer list/detail, training center, early-warning review, usage dashboard, and admin command center.

## Recommended Stack

- Backend: Python, FastAPI, Pydantic, SQLAlchemy or SQLModel, PostgreSQL driver, OpenAI SDK.
- Database: Neon PostgreSQL, optional pgvector later.
- WhatsApp: Meta WhatsApp Cloud API.
- Workers: Python, scheduler/cron first; queue system optional later.
- Frontend: Next.js, TypeScript, Tailwind CSS, shadcn/ui, Recharts.
- AI: OpenAI Responses API, Structured Outputs, embeddings, tool/function calling.

## Core Business Flow

1. Admin registers a customer phone number.
2. Backend saves customer in Neon with status `registered`.
3. WhatsApp bot sends an approved welcome template.
4. Customer replies.
5. Bot forwards inbound message to backend.
6. Backend runs profiling and intent handling.
7. Business details are stored as structured memory.
8. Customer can ask for pricing, HPP, margin, supplier, competitor, market, restock, or general business advice.
9. Worker/agent creates early-warning drafts when rules detect relevant business signals.
10. Admin monitors customer activity, AI cost, knowledge, training examples, and warnings in dashboard.

## Key Domain Standards

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

Warning severities:

```text
info
warning
urgent
```

Warning statuses:

```text
draft
approved
scheduled
sent
skipped
failed
```

## Database Scope

The schema docs define these main table groups:

- Core admin/customer/business/product/message/session tables.
- User memory, recommendations, and AI usage logs.
- Knowledge documents, training examples, bot rules, bot skills, and feedback.
- Early-warning rules and early-warning events.

Suggested migration files:

```text
001_extensions.sql
002_admins_customers_businesses.sql
003_products_messages_sessions.sql
004_memories_recommendations_usage.sql
005_training_knowledge_rules_skills.sql
006_early_warnings.sql
007_indexes.sql
```

## API Scope

Required MVP endpoints:

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

Important contract source: `docs/08-api-contracts.md`.

## AI Design

Do not fine-tune in MVP. Build a training layer first:

- Prompt templates.
- Knowledge base.
- Training examples.
- Rules.
- Skills/tools.
- Feedback loop.
- Usage logging.

AI tasks:

- Intent Router.
- Business Profiler.
- Memory Extractor.
- Answer Composer.
- Admin Query Parser.
- Early Warning Composer.

Model strategy:

- Use cheaper models for routing and extraction.
- Use stronger models for final answers and complex reasoning.
- Use deterministic code for simple calculations.
- Never use AI for arithmetic.

Required deterministic calculators:

```text
calculate_margin(selling_price, hpp)
recommend_price(hpp, target_margin_percent)
```

## Early Warning MVP

Early warning should be relevant, evidence-based, rate-limited, and actionable. MVP should default to:

```text
auto_send = false
```

Workflow:

1. Worker scans active rules and available data.
2. Worker creates warning candidates.
3. System deduplicates and rate-limits by customer and warning type.
4. AI composes customer-specific warning drafts.
5. Admin reviews and approves.
6. System sends approved warnings through WhatsApp.

Anti-spam rules:

- Max 1 early warning per customer per day.
- Max 3 early warnings per customer per week.
- Do not repeat same warning type within 7 days unless severity is urgent.
- Use approved WhatsApp templates when Sorota initiates outbound messages outside the session window.

## Training Center

Training Center lets admins/researchers improve responses without fine-tuning. It should support:

- Knowledge documents.
- Research notes.
- Ideal Q&A examples.
- Bot rules/persona.
- Skills/tools.
- Response feedback.

Response rules:

- Answer in Indonesian.
- Use friendly UMKM tone.
- Avoid long theoretical explanations.
- Include an actionable next step.
- Ask one focused question when data is missing.
- Do not fabricate exact market prices without evidence.
- Mention uncertainty when sources are weak.

## Current Repo Observations

- `backend/`, `frontend/`, `whatsapp-bot/`, `workers/`, and `docs/` exist.
- `database-migrations/` is not present yet.
- Existing `.env.example` files exist for backend, WhatsApp bot, and workers.
- `frontend/AGENTS.md` contains a Next.js warning; root-level project memory did not exist before this report.

## Practical Memory Answer

Codex does not reliably keep invisible project memory across separate sessions. The durable way is to save project context inside the repository:

- `AGENTS.md` for short future-agent instructions.
- `docs/codex-project-report.md` for the fuller project report.
- Existing domain docs in `docs/` remain the source of truth.

Future Codex sessions should read `AGENTS.md` and the relevant docs before implementation, especially `docs/08-api-contracts.md` and `docs/10-codex-execution-instructions.md`.
