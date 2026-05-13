# Sorota AI System

Folder ini berisi semua aset AI untuk platform Sorota: prompt templates, personas, rules, dan examples.

## Struktur

```
prompts/    # Template prompt utama, di-load oleh core-api saat runtime
personas/   # Karakter dan spesialisasi advisor per jenis bisnis
rules/      # Panduan gaya, keamanan, dan etika saran bisnis
examples/   # Contoh respons berkualitas (untuk evaluasi & fine-tuning)
```

## Cara Menggunakan Prompt

Core-api membaca file dari folder ini melalui `AI_SYSTEM_PATH` di `.env`.

Placeholder dalam prompt menggunakan format `{{VARIABLE_NAME}}` dan diganti oleh Go code sebelum dikirim ke AI provider.

### Variabel yang tersedia di `business_advisor.md`

| Placeholder          | Sumber                                 |
|----------------------|----------------------------------------|
| `{{BUSINESS_CONTEXT}}` | Data dari tabel `business_profiles`  |
| `{{CHAT_HISTORY}}`   | 10 pesan terakhir dari sesi chat aktif |
| `{{USER_MESSAGE}}`   | Pesan terbaru dari user                |

## Menambah Prompt Baru

1. Buat file `.md` baru di `prompts/`.
2. Gunakan placeholder `{{VARIABLE_NAME}}` untuk variabel dinamis.
3. Di Go code, panggil `ai.LoadPromptTemplate(path, "nama_file.md", vars)`.
