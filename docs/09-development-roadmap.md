# 09 Development Roadmap

## Phase 0: Standardization

Output:

- Business category list
- Customer status list
- Intent list
- Conversation state list
- Minimum database schema
- Prompt task list

Do this before coding heavily.

## Phase 1: Database foundation

Create migrations for:

```text
admins
customers
businesses
products
whatsapp_messages
chat_sessions
user_memories
ai_usage_logs
```

Use Neon PostgreSQL.

## Phase 2: Backend core

Build:

```text
FastAPI app
Neon DB connection
Customer CRUD
Business CRUD
Message logging
AI usage logging
Health check
```

## Phase 3: WhatsApp bot adapter

Build:

```text
Webhook verification
Inbound message handler
Outbound message sender
Welcome template sender
Forward inbound message to backend
```

## Phase 4: Profiling agent

Build:

```text
Conversation state machine
Business profiler prompt
Memory extractor
Business profile updater
```

## Phase 5: Business assistant MVP

Build skills:

```text
Margin Calculator
Pricing Advisor
HPP Helper
Simple Recommendation
```

## Phase 6: Admin dashboard support APIs

Frontend is manually built by owner, but backend must support:

```text
Customer list
Customer detail
Business mapping
Usage dashboard
Latest messages
```

## Phase 7: Training center backend

Build:

```text
Knowledge CRUD
Training examples CRUD
Bot rules CRUD
Skill settings CRUD
Feedback logging
```

## Phase 8: Early warning MVP

Build:

```text
Early warning rules
Early warning event generator
Admin approval mode
Send approved warning via WhatsApp
Anti-spam/rate limit rules
```

## Phase 9: Workers

Build:

```text
Scheduled jobs
Research digest
Knowledge processing
Trend monitoring placeholders
Market crawling placeholders
```

## Phase 10: MCP later

Only after internal tools are stable, expose:

```text
get_business_profile
get_market_prices
get_researcher_notes
calculate_margin
recommend_price
create_early_warning
```

## Do not build too early

Avoid initially:

```text
Complex multi-agent orchestration
Large crawler system
Fine-tuning
MCP-first architecture
ERP/inventory full system
Marketplace integration
Community feature
```

