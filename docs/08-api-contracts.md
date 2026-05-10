# 08 API Contracts

This document defines initial backend API contracts for frontend, whatsapp-bot, and workers.

## Admin customer APIs

### Create customer

```http
POST /api/customers
```

Request:

```json
{
  "name": "Budi",
  "phone_number": "+628123456789",
  "business_name": "Ayam Geprek Mas Budi",
  "business_category": "kuliner",
  "location": "Bandung"
}
```

Response:

```json
{
  "id": "uuid",
  "status": "registered"
}
```

### List customers

```http
GET /api/customers?status=active&business_category=kuliner
```

Response:

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Budi",
      "phone_number": "+628123456789",
      "status": "active",
      "business_category": "kuliner",
      "last_active_at": "2026-05-10T10:00:00Z"
    }
  ]
}
```

### Get customer detail

```http
GET /api/customers/{customer_id}
```

## WhatsApp internal APIs

### Inbound message

```http
POST /internal/whatsapp/inbound
```

Request:

```json
{
  "phone_number": "+628123456789",
  "message_text": "Saya jual ayam geprek di Bandung",
  "wa_message_id": "wamid.xxx",
  "raw_payload": {}
}
```

Response:

```json
{
  "reply_text": "Mantap Kak. Nama bisnisnya apa ya?",
  "should_send": true,
  "customer_status": "profiling"
}
```

### Send welcome request

```http
POST /internal/whatsapp/send-welcome
```

Request:

```json
{
  "customer_id": "uuid"
}
```

Response:

```json
{
  "status": "queued"
}
```

## Training Center APIs

### Create knowledge document

```http
POST /api/knowledge-documents
```

Request:

```json
{
  "title": "Harga ayam Bandung minggu ini",
  "content": "Harga ayam cenderung naik sekitar 8-12% di beberapa supplier.",
  "category": "market_price",
  "business_category": "kuliner",
  "location": "Bandung",
  "source_type": "researcher_note",
  "confidence_score": 0.8
}
```

### Create training example

```http
POST /api/training-examples
```

Request:

```json
{
  "question": "Harga ayam naik, saya harus naikkan harga jual?",
  "ideal_answer": "Cek dulu dampaknya ke HPP dan margin...",
  "business_category": "kuliner",
  "intent": "pricing_advice",
  "tags": ["ayam", "pricing", "margin"]
}
```

## Admin command API

### Parse and execute admin command

```http
POST /api/admin-command
```

Request:

```json
{
  "command": "Cek customer kuliner yang belum aktif minggu ini"
}
```

Response:

```json
{
  "intent": "customer_search",
  "summary": "Ditemukan 12 customer kuliner yang belum aktif minggu ini.",
  "data": [],
  "suggested_actions": ["Kirim follow-up template"]
}
```

## Early warning APIs

### List early warning events

```http
GET /api/early-warnings?status=draft
```

### Approve early warning

```http
POST /api/early-warnings/{event_id}/approve
```

### Send early warning

```http
POST /api/early-warnings/{event_id}/send
```

