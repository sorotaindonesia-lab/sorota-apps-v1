"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_CORE_API_URL || "http://localhost:8080";

type Role = "assistant" | "user";

interface Message {
  role: Role;
  content: string;
}

interface ProfileDraft {
  business_name: string;
  business_type: string;
  location: string;
  monthly_revenue: number | null;
  monthly_profit: number | null;
  main_products: string;
  main_problem: string;
  target_goal: string;
  selling_price_per_unit: number | null;
  cost_per_unit: number | null;
}

interface ParseResponse {
  draft: ProfileDraft;
  missing_fields: string[];
  next_field: string;
  next_question: string;
  ready_to_save: boolean;
}

const emptyDraft: ProfileDraft = {
  business_name: "",
  business_type: "",
  location: "",
  monthly_revenue: null,
  monthly_profit: null,
  main_products: "",
  main_problem: "",
  target_goal: "",
  selling_price_per_unit: null,
  cost_per_unit: null,
};

const initialQuestion =
  "Halo, saya bantu buat profil bisnis dulu. Ceritakan singkat nama bisnis, jenis usaha, lokasi, dan masalah utama yang ingin dibantu.";

export default function OnboardingPage() {
  const router = useRouter();
  const bottomRef = useRef<HTMLDivElement>(null);
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", content: initialQuestion },
  ]);
  const [draft, setDraft] = useState<ProfileDraft>(emptyDraft);
  const [currentField, setCurrentField] = useState("freeform");
  const [missingFields, setMissingFields] = useState<string[]>([
    "business_name",
    "business_type",
    "location",
    "main_problem",
  ]);
  const [readyToSave, setReadyToSave] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const canSave = useMemo(() => isRequiredComplete(draft), [draft]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const userMessage = input.trim();
    if (!userMessage || loading || saving) return;

    setInput("");
    setError("");
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", content: userMessage }]);

    try {
      const res = await fetch(`${API_URL}/api/v1/onboarding/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
          current_field: currentField,
          draft,
        }),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Gagal membaca jawaban");

      const result = json.data as ParseResponse;
      setDraft(result.draft);
      setCurrentField(result.next_field);
      setMissingFields(result.missing_fields);
      setReadyToSave(result.ready_to_save);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.next_question },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan");
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Maaf, saya belum bisa membaca jawaban itu. Coba tulis lagi dengan lebih singkat.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function saveProfile() {
    if (!canSave || saving) return;

    setSaving(true);
    setError("");

    const userId = crypto.randomUUID();
    const payload = {
      user_id: userId,
      business_name: draft.business_name.trim(),
      business_type: draft.business_type.trim(),
      location: draft.location.trim(),
      monthly_revenue: draft.monthly_revenue,
      monthly_profit: draft.monthly_profit,
      main_products: emptyToNull(draft.main_products),
      main_problem: draft.main_problem.trim(),
      target_goal: emptyToNull(draft.target_goal),
      selling_price_per_unit: draft.selling_price_per_unit,
      cost_per_unit: draft.cost_per_unit,
    };

    try {
      const res = await fetch(`${API_URL}/api/v1/business-profiles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const json = await res.json();
      if (!res.ok) throw new Error(json.error || "Gagal menyimpan profil");

      localStorage.setItem("sorota_user_id", userId);
      localStorage.setItem("sorota_profile_id", json.data.id);
      router.push("/chat");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan");
    } finally {
      setSaving(false);
    }
  }

  function updateDraft<K extends keyof ProfileDraft>(
    key: K,
    value: ProfileDraft[K],
  ) {
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <main className="min-h-screen bg-gray-50 px-4 py-6 sm:px-6 lg:px-8">
      <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[minmax(0,1fr)_400px]">
        <section className="flex min-h-[calc(100vh-3rem)] flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm">
          <div className="border-b border-gray-200 px-5 py-4">
            <p className="text-sm font-semibold text-gray-900">
              Onboarding Sorota
            </p>
            <p className="mt-1 text-sm text-gray-500">
              Jawab natural, nanti Sorota susun profil bisnisnya.
            </p>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto px-4 py-5">
            {messages.map((message, index) => (
              <ChatBubble key={`${message.role}-${index}`} message={message} />
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm text-gray-400">
                  Membaca jawaban...
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          <form
            onSubmit={sendMessage}
            className="border-t border-gray-200 bg-white px-4 py-3"
          >
            {error && <p className="mb-2 text-sm text-red-600">{error}</p>}
            <div className="flex gap-3">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                disabled={loading || saving}
                placeholder="Tulis jawaban Anda..."
                className="min-w-0 flex-1 rounded-full border border-gray-300 px-4 py-2 text-sm text-gray-900 outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-60"
              />
              <button
                type="submit"
                disabled={!input.trim() || loading || saving}
                className="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
              >
                Kirim
              </button>
            </div>
          </form>
        </section>

        <aside className="space-y-4">
          <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-start justify-between gap-4">
              <div>
                <h1 className="text-lg font-bold text-gray-900">
                  Ringkasan Profil
                </h1>
                <p className="mt-1 text-sm text-gray-500">
                  Cek dan edit sebelum disimpan.
                </p>
              </div>
              <StatusBadge ready={readyToSave && canSave} />
            </div>

            <div className="space-y-4">
              <TextField
                label="Nama Bisnis"
                value={draft.business_name}
                required
                onChange={(value) => updateDraft("business_name", value)}
              />
              <TextField
                label="Jenis Bisnis"
                value={draft.business_type}
                required
                onChange={(value) => updateDraft("business_type", value)}
              />
              <TextField
                label="Lokasi"
                value={draft.location}
                required
                onChange={(value) => updateDraft("location", value)}
              />
              <TextAreaField
                label="Masalah Utama"
                value={draft.main_problem}
                required
                onChange={(value) => updateDraft("main_problem", value)}
              />
              <TextField
                label="Produk / Layanan Utama"
                value={draft.main_products}
                onChange={(value) => updateDraft("main_products", value)}
              />

              <div className="grid grid-cols-2 gap-3">
                <NumberField
                  label="Omzet Bulanan"
                  value={draft.monthly_revenue}
                  onChange={(value) => updateDraft("monthly_revenue", value)}
                />
                <NumberField
                  label="Laba Bulanan"
                  value={draft.monthly_profit}
                  onChange={(value) => updateDraft("monthly_profit", value)}
                />
                <NumberField
                  label="Harga Jual / Unit"
                  value={draft.selling_price_per_unit}
                  onChange={(value) =>
                    updateDraft("selling_price_per_unit", value)
                  }
                />
                <NumberField
                  label="HPP / Unit"
                  value={draft.cost_per_unit}
                  onChange={(value) => updateDraft("cost_per_unit", value)}
                />
              </div>

              <TextField
                label="Target Bisnis"
                value={draft.target_goal}
                onChange={(value) => updateDraft("target_goal", value)}
              />
            </div>

            {missingFields.length > 0 && (
              <p className="mt-4 text-sm text-amber-700">
                Masih perlu: {missingFields.map(fieldLabel).join(", ")}.
              </p>
            )}

            <button
              type="button"
              onClick={saveProfile}
              disabled={!canSave || saving}
              className="mt-5 w-full rounded-lg bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
            >
              {saving ? "Menyimpan..." : "Simpan & Mulai Konsultasi"}
            </button>
          </div>

          <div className="rounded-lg border border-blue-100 bg-blue-50 p-4 text-sm text-blue-900">
            {canSave
              ? "Profil minimum sudah siap. Data opsional bisa ditambah sekarang atau nanti lewat chat."
              : "Isi empat data wajib dulu: nama bisnis, jenis bisnis, lokasi, dan masalah utama."}
          </div>
        </aside>
      </div>
    </main>
  );
}

function ChatBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[82%] whitespace-pre-wrap rounded-lg px-4 py-3 text-sm leading-relaxed ${
          isUser
            ? "bg-blue-600 text-white"
            : "border border-gray-200 bg-white text-gray-800"
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}

function StatusBadge({ ready }: { ready: boolean }) {
  return (
    <span
      className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${
        ready ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700"
      }`}
    >
      {ready ? "Siap" : "Draft"}
    </span>
  );
}

function TextField({
  label,
  value,
  required,
  onChange,
}: {
  label: string;
  value: string;
  required?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-gray-700">
        {label} {required && <span className="text-red-500">*</span>}
      </span>
      <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
      />
    </label>
  );
}

function TextAreaField({
  label,
  value,
  required,
  onChange,
}: {
  label: string;
  value: string;
  required?: boolean;
  onChange: (value: string) => void;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-sm font-medium text-gray-700">
        {label} {required && <span className="text-red-500">*</span>}
      </span>
      <textarea
        value={value}
        rows={3}
        onChange={(e) => onChange(e.target.value)}
        className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
      />
    </label>
  );
}

function NumberField({
  label,
  value,
  onChange,
}: {
  label: string;
  value: number | null;
  onChange: (value: number | null) => void;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-gray-700">
        {label}
      </span>
      <input
        type="number"
        value={value ?? ""}
        min={0}
        onChange={(e) => onChange(parseNumberOrNull(e.target.value))}
        placeholder="Rp"
        className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm text-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
      />
    </label>
  );
}

function parseNumberOrNull(value: string): number | null {
  if (!value) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function emptyToNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function isRequiredComplete(draft: ProfileDraft): boolean {
  return Boolean(
    draft.business_name.trim() &&
      draft.business_type.trim() &&
      draft.location.trim() &&
      draft.main_problem.trim(),
  );
}

function fieldLabel(field: string): string {
  const labels: Record<string, string> = {
    business_name: "nama bisnis",
    business_type: "jenis bisnis",
    location: "lokasi",
    main_problem: "masalah utama",
  };
  return labels[field] ?? field;
}
