# Profil dan Lingkungan Uji — P1 (Ritel Kopi)

| Field | Nilai |
| ----- | ----- |
| Profil | P1 — Ritel kopi |
| Dataset | `dataset_1.csv` (`EXTERNAL_DATASET=1`) |
| Branch | `test/loop-correction` |
| Commit | `6870cda` |
| Tanggal uji | 2026-07-16 |
| Health check | `{"status":"ok"}` |
| Baris `business_data` | 3547 |
| Port API | 8000 |
| Harness flags awal | Semua `false` |

## Catatan lingkungan

- Stack Docker: `agent-api`, `pgsql-business`, `pgsql-agent` — Up dan sehat setelah restart API.
- Seeding: `business_data` dari `dataset_1.csv` (3547 baris, 11 kolom).
- Memori agen kosong pada awal uji (`GET /chat/history` → `[]`).
