const API_URL = process.env.NEXT_PUBLIC_CORE_API_URL || "http://localhost:8080";

interface Mentor {
  id: string;
  name: string;
  expertise: string;
  description: string;
  business_background?: string;
  booking_url: string;
  image_url?: string;
}

async function getMentors(): Promise<Mentor[]> {
  try {
    const res = await fetch(`${API_URL}/api/v1/mentors`, {
      next: { revalidate: 3600 },
    });
    if (!res.ok) return [];
    const json = await res.json();
    return json.data ?? [];
  } catch {
    return [];
  }
}

export default async function MentorsPage() {
  const mentors = await getMentors();

  return (
    <main className="min-h-screen bg-gray-50 py-12 px-6">
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Mentor Bisnis</h1>
          <p className="text-gray-600 mt-1">
            Konsultasi lebih dalam dengan mentor berpengalaman di bidangnya.
          </p>
        </div>

        {mentors.length === 0 ? (
          <p className="text-gray-500 text-center py-12">
            Belum ada mentor tersedia saat ini.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {mentors.map((mentor) => (
              <MentorCard key={mentor.id} mentor={mentor} />
            ))}
          </div>
        )}
      </div>
    </main>
  );
}

function MentorCard({ mentor }: { mentor: Mentor }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 flex flex-col gap-4 hover:shadow-md transition-shadow">
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-lg flex-shrink-0">
          {mentor.name.charAt(0)}
        </div>
        <div>
          <h2 className="font-semibold text-gray-900">{mentor.name}</h2>
          <span className="inline-block text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded-full mt-1">
            {mentor.expertise}
          </span>
        </div>
      </div>

      <p className="text-sm text-gray-600 leading-relaxed">{mentor.description}</p>

      {mentor.business_background && (
        <p className="text-xs text-gray-500 italic">{mentor.business_background}</p>
      )}

      <a
        href={mentor.booking_url}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-auto inline-block text-center bg-blue-600 text-white font-medium text-sm py-2.5 px-4 rounded-lg hover:bg-blue-700 transition-colors"
      >
        Book Mentor
      </a>
    </div>
  );
}
