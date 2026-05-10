const { config } = require("./config");

function previewText(value) {
  if (!value) {
    return "";
  }

  return value.length > 2000 ? `${value.slice(0, 2000)}...` : value;
}

function parseJsonResponse(text, response) {
  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch (error) {
    throw new Error(
      `Backend returned non-JSON response (${response.status} ${response.statusText}): ${previewText(text)}`
    );
  }
}

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

  const responseText = await response.text();
  const data = response.headers.get("content-type")?.includes("application/json")
    ? parseJsonResponse(responseText, response)
    : null;

  if (!response.ok) {
    throw new Error(
      data
        ? `Backend inbound failed: ${response.status} ${JSON.stringify(data)}`
        : `Backend inbound failed: ${response.status} ${response.statusText}: ${previewText(responseText)}`
    );
  }

  if (!data) {
    throw new Error(
      `Backend inbound succeeded but did not return JSON (${response.status} ${response.statusText}): ${previewText(responseText)}`
    );
  }

  return data;
}

module.exports = { forwardTelegramInbound };
