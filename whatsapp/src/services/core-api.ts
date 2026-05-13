import axios from "axios";

const coreApiUrl = process.env.CORE_API_URL || "http://localhost:8080";

interface WhatsAppMessagePayload {
  phone_number: string;
  message: string;
}

interface WhatsAppMessageResponse {
  reply: string;
}

export async function sendToApi(
  phoneNumber: string,
  message: string
): Promise<string> {
  const payload: WhatsAppMessagePayload = {
    phone_number: phoneNumber,
    message,
  };

  const response = await axios.post<{ data: WhatsAppMessageResponse }>(
    `${coreApiUrl}/api/v1/whatsapp/message`,
    payload,
    { timeout: 30_000 }
  );

  return response.data.data.reply;
}
