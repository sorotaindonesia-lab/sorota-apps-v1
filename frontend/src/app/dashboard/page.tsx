"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_CORE_API_URL || "http://localhost:8080";

interface BusinessProfile {
  business_name: string;
  business_type: string;
  location: string;
  monthly_revenue?: number;
  monthly_profit?: number;
  main_problem: string;
  target_goal?: string;
}

export default function DashboardPage() {
  const [profile, setProfile] = useState<BusinessProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let ignore = false;

    async function loadProfile() {
      const userId = localStorage.getItem("sorota_user_id");
      if (!userId) {
        if (!ignore) setLoading(false);
        return;
      }

      try {
        const res = await fetch(`${API_URL}/api/v1/business-profiles/${userId}`);
        const json = res.ok ? await res.json() : null;
        if (!ignore) setProfile(json?.data ?? null);
      } catch {
        if (!ignore) setProfile(null);
      } finally {
        if (!ignore) setLoading(false);
      }
    }

    loadProfile();

    return () => {
      ignore = true;
    };
  }, []);

  if (loading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Memuat...</p>
      </main>
    );
  }

  if (!profile) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center gap-4 px-6">
        <p className="text-gray-700 text-center">
          Profil bisnis belum tersedia. Mulai onboarding terlebih dahulu.
        </p>
        <Link
          href="/onboarding"
          className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          Mulai Onboarding
        </Link>
      </main>
    );
  }

  const marginPct =
    profile.monthly_revenue && profile.monthly_profit
      ? ((profile.monthly_profit / profile.monthly_revenue) * 100).toFixed(1)
      : null;

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-6">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>

        {/* Profile summary */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 space-y-3">
          <h2 className="font-semibold text-gray-900 text-lg">
            {profile.business_name}
          </h2>
          <div className="grid grid-cols-2 gap-3 text-sm text-gray-600">
            <Stat label="Jenis Bisnis" value={profile.business_type} />
            <Stat label="Lokasi" value={profile.location} />
            {profile.monthly_revenue && (
              <Stat
                label="Omset Bulanan"
                value={`Rp ${profile.monthly_revenue.toLocaleString("id-ID")}`}
              />
            )}
            {profile.monthly_profit && (
              <Stat
                label="Laba Bulanan"
                value={`Rp ${profile.monthly_profit.toLocaleString("id-ID")}`}
              />
            )}
            {marginPct && <Stat label="Margin" value={`${marginPct}%`} />}
          </div>
          {profile.main_problem && (
            <div className="pt-2 border-t border-gray-100">
              <p className="text-xs text-gray-500 mb-1">Masalah Utama</p>
              <p className="text-sm text-gray-700">{profile.main_problem}</p>
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Link
            href="/chat"
            className="bg-blue-600 text-white rounded-xl p-5 hover:bg-blue-700 transition-colors"
          >
            <p className="font-semibold">Konsultasi AI</p>
            <p className="text-sm text-blue-100 mt-1">
              Tanya Sorota tentang bisnis Anda
            </p>
          </Link>
          <Link
            href="/mentors"
            className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow"
          >
            <p className="font-semibold text-gray-900">Temukan Mentor</p>
            <p className="text-sm text-gray-500 mt-1">
              Konsultasi dengan mentor berpengalaman
            </p>
          </Link>
        </div>
      </div>
    </main>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-xs text-gray-400">{label}</p>
      <p className="text-gray-800 font-medium">{value}</p>
    </div>
  );
}
