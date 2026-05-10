# 05 WhatsApp Bot Flow

## WhatsApp role

WhatsApp bot is only a channel adapter. Main AI logic lives in backend.

## Important WhatsApp rule

If Sorota starts the conversation first, send an approved WhatsApp template message. After customer replies, normal session messages can continue within the allowed service window.

## Flow: admin registers customer

```text
Admin dashboard
↓
POST /customers
↓
Backend creates customer with status registered
↓
Backend asks whatsapp-bot to send welcome template
↓
WhatsApp sends template
↓
Customer status becomes invited
```

## Flow: customer replies

```text
Customer replies on WhatsApp
↓
WhatsApp Cloud API calls webhook
↓
whatsapp-bot verifies webhook
↓
whatsapp-bot POSTs message to backend /internal/whatsapp/inbound
↓
backend processes message
↓
backend returns response
↓
whatsapp-bot sends response to customer
```

## Conversation state machine

```text
NEW
ASK_BUSINESS_NAME
ASK_BUSINESS_CATEGORY
ASK_LOCATION
ASK_MAIN_PRODUCTS
ASK_PRICE_DATA
ACTIVE
```

## Welcome template example

Template name:

```text
sorota_welcome_v1
```

Text:

```text
Halo {{1}}, saya Sorota, AI pendamping bisnis UMKM.

Saya bisa bantu cek harga jual, HPP, margin, supplier, dan insight bisnis harian.

Balas pesan ini untuk mulai.
```

## Profiling messages

### Ask business name

```text
Halo Kak, saya Sorota 👋
Biar saya bisa bantu lebih tepat, boleh tahu nama bisnis Kakak?
```

### Ask category

```text
Bisnis Kakak masuk kategori apa?

1. Kuliner
2. Retail
3. Fashion
4. Laundry
5. Warung / toko kelontong
6. Coffee shop
7. Reseller
8. Lainnya
```

### Ask location

```text
Lokasi bisnis Kakak di kota/area mana?
```

### Ask main product

```text
Produk utama yang paling sering Kakak jual apa?
```

### Active mode confirmation

```text
Siap Kak. Data bisnis awal sudah saya simpan.

Mulai sekarang Kakak bisa tanya soal harga jual, margin, HPP, supplier, atau strategi bisnis harian.
```

## Backend inbound payload

whatsapp-bot should call backend:

```json
{
  "phone_number": "+628123456789",
  "message_text": "Saya jual ayam geprek di Bandung",
  "wa_message_id": "wamid.xxx",
  "raw_payload": {}
}
```

Backend response:

```json
{
  "reply_text": "Mantap Kak. Nama bisnisnya apa ya?",
  "customer_status": "profiling",
  "should_send": true
}
```

