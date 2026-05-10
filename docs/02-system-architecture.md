# 02 System Architecture

## Root folder

```text
sorota/
├── backend/
├── database-migrations/
├── frontend/
├── whatsapp-bot/
├── workers/
├── mcp-servers/
└── docs/
```

## Recommended stack

### Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy / SQLModel
Alembic optional
```

### Database

```text
Neon PostgreSQL
pgvector extension optional for embeddings
```

### WhatsApp

```text
Meta WhatsApp Cloud API
```

### AI

```text
OpenAI Responses API
Structured Outputs
Embeddings
Tool/function calling
```

### Workers

```text
Python worker
Celery/RQ/Arq optional
Redis optional for queue
Cron/scheduler for early warning
```

### Frontend

Frontend dibuat manual oleh owner. Backend harus menyediakan API contract yang jelas untuk frontend.

## Service responsibilities

### backend/

Backend adalah otak utama Sorota.

Responsibilities:

- Customer API
- Business API
- Product API
- Message API
- AI gateway
- Intent router
- Business profiler
- Memory extractor
- Answer composer
- Admin command parser
- Knowledge retrieval
- Usage/cost logging
- Early warning management API

Backend boleh menerima request dari:

- frontend admin dashboard
- whatsapp-bot service
- workers

### whatsapp-bot/

WhatsApp bot adalah channel adapter.

Responsibilities:

- Verify webhook
- Receive WhatsApp messages
- Send WhatsApp template messages
- Send normal WhatsApp messages
- Forward inbound message to backend
- Return backend response to WhatsApp customer

WhatsApp bot tidak boleh melakukan:

- AI reasoning utama
- pricing calculation utama
- direct database manipulation yang kompleks
- customer business decision logic

### workers/

Workers menjalankan background processes.

Responsibilities:

- Early warning scan
- Trend monitoring
- Market price crawling
- Research digest
- Scheduled customer insight
- Knowledge embedding refresh

### mcp-servers/

MCP dipakai setelah internal tools stabil.

Initial MCP candidates:

```text
get_business_profile
get_user_products
calculate_margin
recommend_price
get_market_prices
get_researcher_notes
save_business_insight
create_early_warning
```

MCP tidak wajib untuk MVP pertama.

## High-level runtime flow

### Incoming customer message

```text
Customer WhatsApp
↓
whatsapp-bot webhook
↓
backend /internal/whatsapp/inbound
↓
load customer + business context
↓
intent router
↓
tool/business calculation if needed
↓
answer composer
↓
memory extractor
↓
save message + usage log
↓
return response
↓
whatsapp-bot sends response
```

### Early warning flow

```text
Scheduler/worker
↓
scan market data + customer profiles + rules
↓
generate warning candidates
↓
dedupe and rate limit
↓
compose customer-specific warning
↓
optional admin approval OR auto-send
↓
whatsapp-bot sends warning template/message
↓
log warning event
```

## Environment separation

Use at least:

```text
local
dev
production
```

Every service should have `.env.example`.

