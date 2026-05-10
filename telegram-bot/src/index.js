const http = require("node:http");

const { config } = require("./config");
const { handleRequest } = require("./webhook");

const server = http.createServer(handleRequest);

server.listen(config.appPort, () => {
  console.log(`Sorota Telegram bot listening on http://127.0.0.1:${config.appPort}`);
});
