import { Message } from "whatsapp-web.js";
import { sendToApi } from "../services/core-api";

export async function handleMessage(msg: Message): Promise<void> {
  // Ignore group messages and status updates
  if (msg.isGroupMsg || msg.from === "status@broadcast") {
    return;
  }

  const phoneNumber = msg.from.replace("@c.us", "");
  const userMessage = msg.body.trim();

  if (!userMessage) return;

  console.log(`[WA] Message from ${phoneNumber}: ${userMessage}`);

  try {
    const reply = await sendToApi(phoneNumber, userMessage);
    await msg.reply(reply);
    console.log(`[WA] Replied to ${phoneNumber}`);
  } catch (err) {
    console.error(`[WA] Error processing message from ${phoneNumber}:`, err);
    await msg.reply(
      "Maaf, Sorota sedang tidak bisa menjawab saat ini. Silakan coba lagi dalam beberapa menit."
    );
  }
}
