# Sorota

AI-powered business advisory platform untuk UMKM Indonesia.

Sorota membantu pemilik usaha mengambil keputusan bisnis lebih cepat, lebih tepat, dan lebih praktis — melalui AI Business Advisor yang memahami konteks UMKM Indonesia.

---

## Struktur Monorepo

```
/sorota-apps
├── /frontend            # Next.js app (UI)
├── /core-api            # Golang REST API
├── /database-migrations # SQL migration files + scripts
├── /whatsapp            # WhatsApp bridge service (Node.js)
├── /ai-system           # Prompt templates, personas, rules
├── .gitignore
├── README.md
└── docker-compose.yml
```

---

## Cara Menjalankan

### 1. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local  # isi NEXT_PUBLIC_CORE_API_URL
npm run dev
```

Buka [http://localhost:3000](http://localhost:3000)

### 2. Core API

```bash
cd core-api
cp .env.example .env  # isi DATABASE_URL, dll
go mod tidy
go run cmd/api/main.go
```

API berjalan di [http://localhost:8080](http://localhost:8080)

### 3. Database Migration

```bash
cd database-migrations
cp .env.example .env  # isi DATABASE_URL
make migrate-up       # jalankan semua migration
make seed             # isi data seed (mentors)
```

### 4. WhatsApp Service

```bash
cd whatsapp
npm install
cp .env.example .env  # isi CORE_API_URL
npm run dev
```

Scan QR code yang muncul di terminal dengan WhatsApp.

---

## Environment Variables

### Core API (`core-api/.env`)

| Variable         | Keterangan                                      |
|------------------|-------------------------------------------------|
| `DATABASE_URL`   | PostgreSQL connection string (Neon)             |
| `AI_PROVIDER`    | `mock` atau `openai`                            |
| `OPENAI_API_KEY` | API key OpenAI (jika AI_PROVIDER=openai)        |
| `AI_SYSTEM_PATH` | Path ke folder `/ai-system` (default: ../ai-system) |
| `PORT`           | Port API (default: 8080)                        |

### Frontend (`frontend/.env.local`)

| Variable                  | Keterangan             |
|---------------------------|------------------------|
| `NEXT_PUBLIC_CORE_API_URL` | URL core-api          |

### Database Migration (`database-migrations/.env`)

| Variable       | Keterangan                          |
|----------------|-------------------------------------|
| `DATABASE_URL` | PostgreSQL connection string (Neon) |

### WhatsApp (`whatsapp/.env`)

| Variable        | Keterangan          |
|-----------------|---------------------|
| `CORE_API_URL`  | URL core-api        |

---

## Tech Stack

| Layer      | Tech                          |
|------------|-------------------------------|
| Frontend   | Next.js, TypeScript, Tailwind |
| Backend    | Golang, Chi, PostgreSQL       |
| Database   | PostgreSQL (Neon)             |
| WhatsApp   | Node.js, whatsapp-web.js      |
| AI         | OpenAI API (mock untuk dev)   |
