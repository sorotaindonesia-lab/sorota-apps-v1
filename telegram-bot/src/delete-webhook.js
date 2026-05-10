const { deleteWebhook } = require("./telegram-client");

deleteWebhook()
  .then((result) => {
    console.log("Telegram webhook deleted");
    console.log(result);
  })
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
