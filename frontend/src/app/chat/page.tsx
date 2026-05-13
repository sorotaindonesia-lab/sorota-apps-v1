"use client";

import { useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_CORE_API_URL || "http://localhost:8080";

interface MentorCard {
  name: string;
  expertise: string;
  booking_url: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  mentors?: MentorCard[];
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);
    setLoading(true);

    const userId = localStorage.getItem("sorota_user_id") || "anonymous";

    try {
      const res = await fetch(`${API_URL}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          session_id: sessionId || undefined,
          message: userMessage,
        }),
      });

      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Gagal mendapat respons");

      setSessionId(json.data.session_id);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: json.data.reply,
          mentors: json.data.recommended_mentors ?? [],
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            err instanceof Error
              ? err.message
              : "Maaf, terjadi kesalahan. Silakan coba lagi.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex flex-col h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold">
          S
        </div>
        <div>
          <p className="font-semibold text-gray-900 text-sm">Sorota</p>
          <p className="text-xs text-gray-500">AI Business Advisor</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 text-sm mt-12">
            <p className="text-lg font-medium text-gray-700 mb-2">
              Selamat datang di Sorota!
            </p>
            <p>Tanyakan apapun tentang bisnis Anda.</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className="space-y-3">
            <div
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-blue-600 text-white rounded-br-sm"
                    : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm"
                }`}
              >
                {msg.content}
              </div>
            </div>

            {/* Mentor cards — muncul di bawah pesan AI kalau ada rekomendasi */}
            {msg.mentors && msg.mentors.length > 0 && (
              <div className="flex justify-start">
                <div className="max-w-[75%] space-y-2">
                  {msg.mentors.map((mentor) => (
                    <MentorCardComponent key={mentor.name} mentor={mentor} />
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-bl-sm">
              <span className="text-gray-400 text-sm">Sorota sedang berpikir...</span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="bg-white border-t border-gray-200 px-4 py-3">
        <form onSubmit={sendMessage} className="flex gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tanyakan tentang bisnis Anda..."
            disabled={loading}
            className="flex-1 border border-gray-300 rounded-full px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-blue-600 text-white px-5 py-2 rounded-full text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            Kirim
          </button>
        </form>
      </div>
    </main>
  );
}

function MentorCardComponent({ mentor }: { mentor: MentorCard }) {
  return (
    <div className="bg-blue-50 border border-blue-100 rounded-xl px-4 py-3 flex items-center justify-between gap-4">
      <div>
        <p className="text-sm font-semibold text-gray-900">{mentor.name}</p>
        <p className="text-xs text-blue-700 mt-0.5">{mentor.expertise}</p>
      </div>
      <a
        href={mentor.booking_url}
        target="_blank"
        rel="noopener noreferrer"
        className="shrink-0 bg-blue-600 text-white text-xs font-medium px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors"
      >
        Book Mentor
      </a>
    </div>
  );
}
