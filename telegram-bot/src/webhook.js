const { forwardTelegramInbound } = require("./backend-client");
const { config } = require("./config");
const { sendMessage } = require("./telegram-client");

async function readJson(request) {
  const chunks = [];
  for await (const chunk of request) {
    chunks.push(chunk);
  }

  const body = Buffer.concat(chunks).toString("utf8");
  if (!body) {
    return {};
  }

  return JSON.parse(body);
}

function sendJson(response, statusCode, payload) {
  response.writeHead(statusCode, { "content-type": "application/json" });
  response.end(JSON.stringify(payload));
}

function isWebhookAuthorized(request) {
  if (!config.telegramWebhookSecret) {
    return true;
  }

  return request.headers["x-telegram-bot-api-secret-token"] === config.telegramWebhookSecret;
}

function toBackendPayload(update) {
  const message = update.message;
  const from = message.from || {};
  const chat = message.chat || {};

  return {
    telegram_user_id: from.id ? String(from.id) : null,
    chat_id: String(chat.id),
    username: from.username || null,
    first_name: from.first_name || null,
    last_name: from.last_name || null,
    message_text: message.text || null,
    telegram_message_id: message.message_id ? String(message.message_id) : null,
    raw_payload: update
  };
}

async function handleTelegramWebhook(request, response) {
  if (!isWebhookAuthorized(request)) {
    sendJson(response, 401, { ok: false, error: "unauthorized" });
    return;
  }

  const update = await readJson(request);
  const message = update.message;

  if (!message || !message.chat || !message.text) {
    sendJson(response, 200, { ok: true, skipped: true });
    return;
  }

  const backendResponse = await forwardTelegramInbound(toBackendPayload(update));
  if (backendResponse.should_send && backendResponse.reply_text) {
    await sendMessage(message.chat.id, backendResponse.reply_text);
  }

  sendJson(response, 200, { ok: true });
}

async function handleRequest(request, response) {
  try {
    const url = new URL(request.url, `http://${request.headers.host || "localhost"}`);

    if (request.method === "GET" && url.pathname === "/health") {
      sendJson(response, 200, { status: "ok", app: "sorota-telegram-bot", environment: config.appEnv });
      return;
    }

    if (request.method === "POST" && url.pathname === config.telegramWebhookPath) {
      await handleTelegramWebhook(request, response);
      return;
    }

    sendJson(response, 404, { ok: false, error: "not found" });
  } catch (error) {
    console.error("Telegram webhook handling failed");
    console.error(error);
    sendJson(response, 500, { ok: false, error: "internal server error" });
  }
}

module.exports = { handleRequest };
