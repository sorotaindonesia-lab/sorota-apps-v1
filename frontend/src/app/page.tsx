import Link from "next/link";

export default function LandingPage() {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-white px-6">
      <div className="max-w-2xl w-full text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-4xl font-bold tracking-tight text-gray-900 sm:text-5xl">
            AI Business Advisor untuk UMKM Indonesia
          </h1>
          <p className="text-lg text-gray-600">
            Sorota membantu pemilik usaha mengambil keputusan bisnis lebih
            cepat, lebih tepat, dan lebih praktis.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/onboarding"
            className="inline-block bg-blue-600 text-white font-semibold px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Coba Konsultasi Bisnis
          </Link>
          <Link
            href="/mentors"
            className="inline-block border border-gray-300 text-gray-700 font-semibold px-8 py-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Temukan Mentor
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-8 text-left">
          {[
            {
              title: "Analisa Bisnis",
              desc: "Pahami kondisi keuangan dan operasional bisnis Anda.",
            },
            {
              title: "Saran Praktis",
              desc: "Langkah konkret yang bisa langsung dijalankan.",
            },
            {
              title: "Terhubung ke Mentor",
              desc: "Konsultasi lebih dalam dengan mentor berpengalaman.",
            },
          ].map((item) => (
            <div
              key={item.title}
              className="p-4 border border-gray-200 rounded-lg"
            >
              <h3 className="font-semibold text-gray-900 mb-1">{item.title}</h3>
              <p className="text-sm text-gray-600">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
