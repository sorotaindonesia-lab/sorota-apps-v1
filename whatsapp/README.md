# Sorota WhatsApp Service

Bridge service yang menghubungkan WhatsApp dengan Sorota core-api.

## Setup

```bash
npm install
cp .env.example .env
# Edit .env, isi CORE_API_URL
npm run dev
```

Scan QR code yang muncul di terminal dengan aplikasi WhatsApp.

## Flow

1. Service start → tampilkan QR code
2. User scan → authenticated
3. User kirim pesan ke nomor WA → handler menerima
4. Handler kirim ke `POST /api/v1/whatsapp/message` di core-api
5. core-api proses dengan AI → kirim balik reply
6. Service kirim reply ke user WhatsApp

## Notes

- Session tersimpan di `.wwebjs_auth/` — jadi tidak perlu scan ulang setiap restart
- Hanya melayani pesan 1-1, bukan grup
- Untuk production, ganti ke WhatsApp Business API
