const { config } = require("./config");
const { setWebhook } = require("./telegram-client");

setWebhook()
  .then((result) => {
    console.log("Telegram webhook set");
    console.log(`Webhook URL: ${config.telegramWebhookUrl}${config.telegramWebhookPath}`);
    console.log(result);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
