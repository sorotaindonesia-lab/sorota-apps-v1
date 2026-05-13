# Sorota Database Migrations

SQL migration files untuk PostgreSQL (Neon).

## Setup

```bash
cp .env.example .env
# Edit .env, isi DATABASE_URL
```

## Commands

```bash
make migrate-up    # jalankan semua migration
make migrate-down  # rollback semua migration
make reset         # reset + migrate ulang
make seed          # isi data awal (mentors, dll)
```

## Struktur

```
migrations/   # up/down SQL files (urutan numerik)
schema/       # full schema reference (tidak dijalankan langsung)
scripts/      # shell scripts untuk tiap command
seeds/        # data awal untuk development
```
