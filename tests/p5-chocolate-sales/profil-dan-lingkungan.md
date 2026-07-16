# Profil dan Lingkungan Uji — P5 (Chocolate Sales)

| Field | Nilai |
| ----- | ----- |
| Profil | P5 — Chocolate sales |
| Dataset | `dataset_5.csv` (`EXTERNAL_DATASET=5`) |
| Branch | `test/loop-correction` |
| Commit | `1e9d9f7` |
| Tanggal uji | 2026-07-16 |
| Health check | `{"status":"ok"}` |
| Baris `business_data` | 1094 |
| Kolom | 6 |
| Port API | 8000 |
| Harness flags akhir | Semua `false` |

## Catatan lingkungan

- Stack Docker: `agent-api`, `pgsql-business`, `pgsql-agent` — Up dan sehat.
- Seeding: `business_data` dari `dataset_5.csv` (1094 baris, 6 kolom: `sales_person`, `country`, `product`, `date`, `amount`, `boxes_shipped`).
- Memori agen kosong pada awal uji (`GET /chat/history` → `[]`).
- Masukan uji dirancang berbasis tujuan skenario (domain penjualan cokelat), bukan translasi pertanyaan P1–P4.
