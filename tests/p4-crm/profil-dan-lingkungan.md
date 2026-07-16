# Profil dan Lingkungan Uji — P4 (CRM / Churn)

| Field | Nilai |
| ----- | ----- |
| Profil | P4 — CRM / churn |
| Dataset | `dataset_4.csv` (`EXTERNAL_DATASET=4`) |
| Branch | `test/loop-correction` |
| Commit | `61dbfa1` |
| Tanggal uji | 2026-07-16 |
| Health check | `{"status":"ok"}` |
| Baris `business_data` | 10000 |
| Kolom | 10 |
| Port API | 8000 |
| Harness flags akhir | Semua `false` |

## Catatan lingkungan

- Stack Docker: `agent-api`, `pgsql-business`, `pgsql-agent` — Up dan sehat.
- Seeding: `business_data` dari `dataset_4.csv` (10000 baris, 10 kolom).
- Memori agen kosong pada awal uji (`GET /chat/history` → `[]`).
- Masukan uji dirancang berbasis tujuan skenario (domain CRM), bukan translasi pertanyaan P1–P3.
