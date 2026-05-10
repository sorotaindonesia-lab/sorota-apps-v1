# 06 Early Warning Agent

## Purpose

Early Warning Agent mengirim informasi penting kepada customer sebelum customer bertanya.

Contoh use case:

- Harga bahan baku naik.
- Trend produk tertentu meningkat.
- Margin produk customer berisiko turun.
- Supplier alternatif lebih murah ditemukan.
- Restock perlu dipertimbangkan.
- Kompetitor sekitar menurunkan/menaikkan harga.
- Ada perubahan pola permintaan musiman.

## Principle

Early warning harus:

- Relevan dengan kategori bisnis customer.
- Punya evidence atau alasan.
- Tidak terlalu sering.
- Memberi tindakan konkret.
- Bisa di-review admin jika mode auto-send dimatikan.

## Flow

```text
Worker scheduler runs every X hours
↓
Load active early warning rules
↓
Load market/trend/research data
↓
Find affected customer segments
↓
Generate warning candidates
↓
Dedupe by customer + warning type
↓
Rate limit per customer
↓
Compose message with AI
↓
Create early_warning_events
↓
If auto_send true, send via WhatsApp
↓
Log sent_at/status
```

## Warning severity

```text
info
warning
urgent
```

## Warning statuses

```text
draft
approved
scheduled
sent
skipped
failed
```

## Example warning types

```text
raw_material_price_rise
margin_risk
supplier_opportunity
trend_opportunity
competitor_price_change
seasonal_demand
restock_risk
```

## Example rules

### Rule: ayam price increase for culinary customers

```json
{
  "name": "Kenaikan harga ayam untuk bisnis kuliner",
  "business_category": "kuliner",
  "rule_type": "raw_material_price_rise",
  "threshold_config": {
    "ingredient": "ayam",
    "increase_percent_min": 8,
    "lookback_days": 7
  }
}
```

### Rule: margin risk

```json
{
  "name": "Margin turun di bawah target",
  "rule_type": "margin_risk",
  "threshold_config": {
    "min_margin_gap_percent": -3
  }
}
```

## Early warning message style

Good:

```text
Kak, ada indikasi harga ayam naik sekitar minggu ini. Kalau ayam geprek adalah produk utama, sebaiknya cek ulang HPP hari ini.

Kalau HPP naik lebih dari 10%, harga jual Rp18.000 mungkin mulai tipis. Coba pertimbangkan harga Rp19.000-Rp20.000 atau cari supplier alternatif.
```

Bad:

```text
Harga pasar berubah. Silakan lakukan analisis bisnis.
```

## Anti-spam rules

- Max 1 early warning per customer per day.
- Max 3 early warnings per customer per week.
- Do not send same warning type twice within 7 days unless severity urgent.
- Do not send outside allowed WhatsApp policy/session unless using approved template.
- For outbound initiated messages, use approved WhatsApp template.

## Admin approval mode

MVP can start with:

```text
auto_send = false
```

Flow:

```text
Agent creates draft warning
↓
Admin reviews in dashboard
↓
Admin approves
↓
System sends warning
```

Later:

```text
auto_send = true for low-risk info messages
admin approval required for urgent or promotional messages
```

