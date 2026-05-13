# Sorota Core API

REST API backend untuk platform Sorota. Dibangun dengan Go + Chi.

## Menjalankan

```bash
cp .env.example .env
# Edit .env, isi DATABASE_URL minimal
go mod tidy
go run cmd/api/main.go
```

## Endpoints

| Method | Path                                    | Keterangan                  |
|--------|-----------------------------------------|-----------------------------|
| GET    | /health                                 | Health check                |
| POST   | /api/v1/business-profiles               | Buat profil bisnis          |
| GET    | /api/v1/business-profiles/:user_id      | Ambil profil bisnis         |
| PUT    | /api/v1/business-profiles/:id           | Update profil bisnis        |
| POST   | /api/v1/chat                            | Kirim pesan ke AI           |
| GET    | /api/v1/chat/sessions/:user_id          | List sesi chat              |
| GET    | /api/v1/chat/messages/:session_id       | List pesan dalam sesi       |
| GET    | /api/v1/mentors                         | List mentor                 |
| POST   | /api/v1/whatsapp/message                | Terima pesan dari WhatsApp  |

## AI Provider

Set `AI_PROVIDER=mock` untuk development (tidak butuh API key).
Set `AI_PROVIDER=openai` dan isi `OPENAI_API_KEY` untuk production.
