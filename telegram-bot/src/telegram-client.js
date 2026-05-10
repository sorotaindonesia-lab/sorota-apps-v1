const { config } = require("./config");

async function telegramRequest(method, body) {
  const response = await fetch(`${config.telegramApiBaseUrl}/bot${config.telegramBotToken}/${method}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body)
  });

  const data = await response.json();
  if (!response.ok || data.ok !== true) {
    throw new Error(`Telegram ${method} failed: ${JSON.stringify(data)}`);
  }

  return data.result;
}

async function sendMessage(chatId, text) {
  return telegramRequest("sendMessage", {
    chat_id: chatId,
    text
  });
}

async function setWebhook() {
  const webhookUrl = `${config.telegramWebhookUrl}${config.telegramWebhookPath}`;
  const payload = {
    url: webhookUrl,
    allowed_updates: ["message"]
  };

  if (config.telegramWebhookSecret) {
    payload.secret_token = config.telegramWebhookSecret;
  }

  return telegramRequest("setWebhook", payload);
}

async function deleteWebhook() {
  return telegramRequest("deleteWebhook", { drop_pending_updates: false });
}

module.exports = { deleteWebhook, sendMessage, setWebhook };
