"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const API_URL = process.env.NEXT_PUBLIC_CORE_API_URL || "http://localhost:8080";

export default function OnboardingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const form = e.currentTarget;
    const get = (name: string) =>
      (form.elements.namedItem(name) as HTMLInputElement).value;

    const data = {
      user_id: crypto.randomUUID(),
      business_name: get("business_name"),
      business_type: get("business_type"),
      location: get("location"),
      monthly_revenue: parseFloatOrNull(get("monthly_revenue")),
      monthly_profit: parseFloatOrNull(get("monthly_profit")),
      main_products: get("main_products") || null,
      main_problem: get("main_problem"),
      target_goal: get("target_goal") || null,
      selling_price_per_unit: parseFloatOrNull(get("selling_price_per_unit")),
      cost_per_unit: parseFloatOrNull(get("cost_per_unit")),
    };

    try {
      const res = await fetch(`${API_URL}/api/v1/business-profiles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!res.ok) {
        const json = await res.json();
        throw new Error(json.error || "Gagal menyimpan profil");
      }

      const json = await res.json();
      localStorage.setItem("sorota_user_id", data.user_id);
      localStorage.setItem("sorota_profile_id", json.data.id);
      router.push("/chat");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Terjadi kesalahan");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-6">
      <div className="max-w-xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Profil Bisnis Anda</h1>
          <p className="text-gray-600 mt-1">
            Ceritakan bisnis Anda agar Sorota bisa memberi saran yang tepat.
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 space-y-5"
        >
          <Field label="Nama Bisnis" name="business_name" required placeholder="Contoh: Warung Kopi Pak Joko" />
          <Field label="Jenis Bisnis" name="business_type" required placeholder="Contoh: Kafe, Laundry, Toko Kelontong" />
          <Field label="Lokasi" name="location" required placeholder="Contoh: Semarang, Jawa Tengah" />
          <Field label="Produk / Layanan Utama" name="main_products" placeholder="Contoh: Kopi susu, jus, snack" />

          {/* Keuangan bulanan */}
          <div className="grid grid-cols-2 gap-4">
            <Field label="Omset Bulanan (Rp)" name="monthly_revenue" type="number" placeholder="15000000" />
            <Field label="Laba Bulanan (Rp)" name="monthly_profit" type="number" placeholder="3000000" />
          </div>

          {/* HPP per unit — data kunci untuk analisa AI */}
          <div className="pt-1 border-t border-gray-100">
            <p className="text-xs text-gray-500 mb-3">
              Opsional tapi sangat membantu — Sorota bisa langsung analisa margin tanpa perlu tanya ulang.
            </p>
            <div className="grid grid-cols-2 gap-4">
              <Field
                label="Harga Jual per Unit (Rp)"
                name="selling_price_per_unit"
                type="number"
                placeholder="Contoh: 15000"
              />
              <Field
                label="Modal / HPP per Unit (Rp)"
                name="cost_per_unit"
                type="number"
                placeholder="Contoh: 8000"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Masalah Utama Bisnis <span className="text-red-500">*</span>
            </label>
            <textarea
              name="main_problem"
              required
              rows={3}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Contoh: Omset stagnan 3 bulan terakhir, tidak tahu cara promosi yang efektif"
            />
          </div>

          <Field
            label="Target / Tujuan Bisnis"
            name="target_goal"
            placeholder="Contoh: Buka cabang kedua dalam 6 bulan"
          />

          {error && <p className="text-red-600 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white font-semibold py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-60"
          >
            {loading ? "Menyimpan..." : "Mulai Konsultasi"}
          </button>
        </form>
      </div>
    </main>
  );
}

function Field({
  label,
  name,
  required,
  placeholder,
  type = "text",
}: {
  label: string;
  name: string;
  required?: boolean;
  placeholder?: string;
  type?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      <input
        type={type}
        name={name}
        required={required}
        placeholder={placeholder}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>
  );
}

function parseFloatOrNull(v: string): number | null {
  const n = parseFloat(v);
  return isNaN(n) ? null : n;
}
