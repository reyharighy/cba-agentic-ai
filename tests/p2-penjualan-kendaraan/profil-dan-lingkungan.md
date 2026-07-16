# Profil dan Lingkungan Uji — P2 (Penjualan Kendaraan)

| Field | Nilai |
| ----- | ----- |
| Profil | P2 — Penjualan kendaraan |
| Dataset | `dataset_2.csv` (`EXTERNAL_DATASET=2`) |
| Branch | `test/loop-correction` |
| Commit | `2e2fe69` |
| Tanggal uji | 2026-07-16 |
| Health check | `{"status":"ok"}` |
| Baris `business_data` | 558837 |
| Kolom | 16 |
| Port API | 8000 |
| Harness flags akhir | Semua `false` |

## Catatan lingkungan

- Stack Docker: `agent-api`, `pgsql-business`, `pgsql-agent` — Up dan sehat.
- Seeding: `business_data` dari `dataset_2.csv` (558837 baris, 16 kolom).
- Memori agen kosong pada awal uji (`GET /chat/history` → `[]`).
- Masukan uji dirancang ulang berbasis tujuan skenario (domain kendaraan), bukan translasi pertanyaan P1.
