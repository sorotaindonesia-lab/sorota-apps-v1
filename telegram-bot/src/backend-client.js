const { config } = require("./config");

async function forwardTelegramInbound(payload) {
  const headers = { "content-type": "application/json" };
  if (config.backendInternalApiKey) {
    headers["x-internal-api-key"] = config.backendInternalApiKey;
  }

  const response = await fetch(`${config.backendBaseUrl}/internal/telegram/inbound`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload)
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(`Backend inbound failed: ${response.status} ${JSON.stringify(data)}`);
  }

  return data;
}

module.exports = { forwardTelegramInbound };
