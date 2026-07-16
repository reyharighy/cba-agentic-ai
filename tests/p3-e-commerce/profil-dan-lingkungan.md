# Profil dan Lingkungan Uji — P3 (E-commerce)

| Field | Nilai |
| ----- | ----- |
| Profil | P3 — E-commerce |
| Dataset | `dataset_3.csv` (`EXTERNAL_DATASET=3`) |
| Branch | `test/loop-correction` |
| Commit | `652f305` |
| Tanggal uji | 2026-07-16 |
| Health check | `{"status":"ok"}` |
| Baris `business_data` | 3500 |
| Kolom | 7 |
| Port API | 8000 |
| Harness flags akhir | Semua `false` |

## Catatan lingkungan

- Stack Docker: `agent-api`, `pgsql-business`, `pgsql-agent` — Up dan sehat.
- Seeding: `business_data` dari `dataset_3.csv` (3500 baris, 7 kolom).
- Memori agen kosong pada awal uji (`GET /chat/history` → `[]`).
- Masukan uji dirancang berbasis tujuan skenario (domain e-commerce), bukan translasi pertanyaan P1/P2.
