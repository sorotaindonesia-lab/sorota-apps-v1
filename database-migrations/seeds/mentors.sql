INSERT INTO mentors (name, expertise, description, business_background, booking_url, image_url)
VALUES
(
    'Budi Santoso',
    'F&B & Kuliner',
    'Berpengalaman 15 tahun di industri F&B. Membantu UMKM kuliner meningkatkan profitabilitas dan memperluas jangkauan pasar.',
    'Founder jaringan restoran lokal dengan 12 cabang di Jawa Tengah.',
    'https://calendly.com/budi-santoso',
    NULL
),
(
    'Siti Rahayu',
    'Retail & Fashion',
    'Spesialis bisnis retail dan fashion lokal. Ahli dalam manajemen stok, pricing strategy, dan pengembangan brand.',
    'Pernah membangun brand fashion lokal hingga masuk ke marketplace nasional.',
    'https://calendly.com/siti-rahayu',
    NULL
),
(
    'Agus Prasetyo',
    'Digital Marketing & E-Commerce',
    'Membantu UMKM masuk ke era digital. Fokus pada strategi pemasaran online, SEO, dan optimasi toko di marketplace.',
    'Konsultan digital marketing dengan pengalaman 10 tahun membantu 200+ UMKM.',
    'https://calendly.com/agus-prasetyo',
    NULL
),
(
    'Dewi Kusuma',
    'Keuangan & Pembukuan UMKM',
    'Ahli keuangan untuk UMKM. Membantu pemilik usaha memahami laporan keuangan, cash flow, dan strategi pendanaan.',
    'Akuntan publik yang kini fokus mendampingi UMKM naik kelas.',
    'https://calendly.com/dewi-kusuma',
    NULL
)
ON CONFLICT DO NOTHING;
