import "dotenv/config";
import { createClient } from "./client";
import { handleMessage } from "./handlers/message-handler";

const client = createClient();

client.on("message", handleMessage);

client.initialize().catch((err) => {
  console.error("[Sorota WA] Failed to initialize:", err);
  process.exit(1);
});
