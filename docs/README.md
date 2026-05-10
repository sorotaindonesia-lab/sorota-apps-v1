# Sorota Project Docs

Dokumen ini adalah brief teknis untuk membangun Sorota: AI pendamping keputusan bisnis UMKM via WhatsApp, dengan admin dashboard, training center, business memory, early warning agent, dan knowledge/research pipeline.

## Urutan baca yang disarankan

1. `01-product-and-business-process.md`
2. `02-system-architecture.md`
3. `03-database-neon-schema.md`
4. `04-ai-agent-design.md`
5. `05-whatsapp-bot-flow.md`
6. `06-early-warning-agent.md`
7. `07-training-center-and-knowledge.md`
8. `08-api-contracts.md`
9. `09-development-roadmap.md`
10. `10-codex-execution-instructions.md`

## Root folder project

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

## Prinsip utama

- WhatsApp adalah channel utama customer.
- Frontend adalah admin dashboard, bukan customer chat utama.
- Backend adalah otak bisnis dan AI.
- WhatsApp bot hanya adapter channel.
- Neon PostgreSQL adalah database utama.
- OpenAI adalah AI provider utama.
- Worker menjalankan background jobs seperti early warning, trend monitoring, crawling, dan digest.
- MCP dipakai nanti setelah tool boundary stabil.

