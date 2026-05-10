# Sorota Telegram Bot

Telegram channel adapter for Sorota. It receives Telegram webhook updates, forwards inbound text messages to the backend, and sends the backend reply back to Telegram.

## Setup

Create `telegram-bot/.env` from `.env.example`:

```text
APP_PORT=3002
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=https://your-ngrok-url
TELEGRAM_WEBHOOK_PATH=/webhook
TELEGRAM_WEBHOOK_SECRET=replace_with_random_secret
BACKEND_BASE_URL=http://localhost:8000
BACKEND_INTERNAL_API_KEY=replace_with_same_internal_api_key
```

Run backend first:

```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```

Run Telegram adapter:

```powershell
cd telegram-bot
npm run dev
```

Register webhook with Telegram:

```powershell
cd telegram-bot
npm run set-webhook
```

Your webhook URL will be:

```text
{TELEGRAM_WEBHOOK_URL}{TELEGRAM_WEBHOOK_PATH}
```

Example:

```text
https://your-ngrok-url/webhook
```

## Notes

- Do not commit `.env`.
- If the bot token has been exposed, rotate it in BotFather.
- This adapter currently handles private text messages first.

## Profiling Test Flow

After backend, ngrok, and the Telegram adapter are running, message the bot:

```text
Halo
```

Expected flow:

```text
Bot asks business name
User sends business name
Bot asks business category
User sends category number or text, for example 1 or kuliner
Bot asks location
User sends city/area
Bot asks main products
User sends products, for example ayam geprek, es teh
Bot confirms the profile is active
```

Run `.\.venv\Scripts\alembic.exe upgrade head` in `backend/` before testing if your database was created before the profiling state machine was added.
