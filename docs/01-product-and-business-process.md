# 01 Product and Business Process

## Product positioning

Sorota adalah AI pendamping keputusan bisnis harian untuk UMKM Indonesia. Produk ini membantu customer mengambil keputusan terkait harga jual, HPP, margin, supplier, kompetitor, trend pasar, restock, dan rekomendasi bisnis.

Chat bukan produk utama. Chat hanya interface. Produk utama adalah business decision engine berbasis data customer, data pasar, knowledge researcher, dan reasoning AI.

## Primary user

- Admin Sorota
- Customer UMKM via WhatsApp
- Researcher internal

## Main business process

```text
Admin mendaftarkan nomor customer
↓
Sistem menyimpan customer ke Neon
↓
Bot WhatsApp mengirim sapaan/template awal
↓
Customer membalas
↓
Bot melakukan profiling bisnis lewat chat
↓
AI memetakan kategori bisnis, lokasi, produk, dan kebutuhan customer
↓
Data bisnis disimpan sebagai structured memory
↓
Customer bisa konsultasi bisnis via WhatsApp
↓
Worker/agent mengirim early warning bila ada insight penting
↓
Admin memantau semuanya di dashboard
```

## Admin workflow

Admin dashboard harus mendukung:

- Tambah customer baru.
- Melihat status customer.
- Melihat kategori bisnis customer.
- Melihat aktivitas chat.
- Melihat estimasi biaya AI.
- Menginput knowledge/research.
- Memberikan contoh jawaban ideal.
- Mengatur skills assistant.
- Mengirim template/follow-up jika perlu.
- Melihat early warning yang dikirim ke customer.

## Customer workflow via WhatsApp

Customer tidak perlu login ke aplikasi.

Flow:

1. Customer menerima sapaan Sorota.
2. Customer membalas.
3. Bot bertanya nama bisnis.
4. Bot bertanya kategori bisnis.
5. Bot bertanya lokasi.
6. Bot bertanya produk utama.
7. Bot bertanya data harga/HPP jika relevan.
8. Bot masuk mode active assistant.

## Customer statuses

```text
registered = nomor sudah didaftarkan admin
invited = bot sudah kirim sapaan/template
profiling = customer sedang dalam proses ditanya profil bisnis
active = customer sudah bisa konsultasi bisnis
inactive = customer tidak aktif dalam periode tertentu
blocked = customer tidak boleh dikontak
invalid = nomor gagal/invalid
```

## Business categories standard

```text
kuliner
retail
fashion
laundry
warung
toko_kelontong
coffee_shop
reseller
jasa
lainnya
```

## Customer intent standard

```text
business_profiling
pricing_advice
margin_calculation
hpp_calculation
supplier_search
market_price_check
competitor_check
product_recommendation
restock_advice
early_warning_explanation
general_business_advice
non_business
```

## MVP definition

MVP sukses jika:

- Admin bisa mendaftarkan nomor customer.
- Bot bisa menyapa customer via WhatsApp.
- Bot bisa melakukan profiling dasar.
- Bot bisa menyimpan data customer dan bisnis ke Neon.
- Customer bisa bertanya soal margin/pricing sederhana.
- Admin bisa melihat customer, status, kategori bisnis, dan aktivitas.
- Sistem mencatat token, latency, dan estimasi biaya AI.
- Early warning agent bisa membuat draft atau mengirim notifikasi berdasarkan rule sederhana.

