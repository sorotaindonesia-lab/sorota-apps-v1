const fs = require("node:fs");
const path = require("node:path");

function loadEnv() {
  const envPath = path.resolve(process.cwd(), ".env");
  if (!fs.existsSync(envPath)) {
    return;
  }

  const content = fs.readFileSync(envPath, "utf8");
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) {
      continue;
    }

    const separatorIndex = trimmed.indexOf("=");
    if (separatorIndex === -1) {
      continue;
    }

    const key = trimmed.slice(0, separatorIndex).trim();
    const value = trimmed.slice(separatorIndex + 1).trim().replace(/^["']|["']$/g, "");
    if (!(key in process.env)) {
      process.env[key] = value;
    }
  }
}

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} is required`);
  }
  return value;
}

function trimTrailingSlash(value) {
  return value.replace(/\/+$/, "");
}

loadEnv();

const config = {
  appEnv: process.env.APP_ENV || "local",
  appPort: Number(process.env.APP_PORT || 3002),
  telegramBotToken: requireEnv("TELEGRAM_BOT_TOKEN"),
  telegramWebhookUrl: trimTrailingSlash(requireEnv("TELEGRAM_WEBHOOK_URL")),
  telegramWebhookPath: process.env.TELEGRAM_WEBHOOK_PATH || "/webhook",
  telegramWebhookSecret: process.env.TELEGRAM_WEBHOOK_SECRET || "",
  telegramApiBaseUrl: trimTrailingSlash(process.env.TELEGRAM_API_BASE_URL || "https://api.telegram.org"),
  backendBaseUrl: trimTrailingSlash(process.env.BACKEND_BASE_URL || "http://localhost:8000"),
  backendInternalApiKey: process.env.BACKEND_INTERNAL_API_KEY || "",
  logLevel: process.env.LOG_LEVEL || "INFO"
};

module.exports = { config };
