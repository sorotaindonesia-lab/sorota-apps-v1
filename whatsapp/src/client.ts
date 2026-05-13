import { Client, LocalAuth } from "whatsapp-web.js";
import qrcode from "qrcode-terminal";

export function createClient(): Client {
  const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    },
  });

  client.on("qr", (qr) => {
    console.log("\n[Sorota WA] Scan QR code below with WhatsApp:\n");
    qrcode.generate(qr, { small: true });
  });

  client.on("authenticated", () => {
    console.log("[Sorota WA] Authenticated");
  });

  client.on("auth_failure", (msg) => {
    console.error("[Sorota WA] Authentication failed:", msg);
  });

  client.on("ready", () => {
    console.log("[Sorota WA] Client is ready. Listening for messages...");
  });

  client.on("disconnected", (reason) => {
    console.warn("[Sorota WA] Disconnected:", reason);
  });

  return client;
}
