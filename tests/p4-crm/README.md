# P4 — CRM / Churn

Laporan pengujian skenario S1–S8 pada profil **P4** (`dataset_4.csv`, domain CRM / churn pelanggan).

## Lingkungan

| Item | Nilai |
| ---- | ----- |
| `EXTERNAL_DATASET` | `4` |
| CSV | `docker_script/datasets/dataset_4.csv` |
| Tabel | `business_data` (default) |
| Branch uji | `test/loop-correction` |

## Pre-flight (sebelum eksekusi)

1. Pastikan `dataset_4.csv` ada secara lokal (~10.000 baris).
2. Set di `.env`:
   ```env
   EXTERNAL_DATASET=4
   ENABLE_EXTERNAL_DB_SEEDING=true
   SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE=false
   SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=false
   SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT=false
   LANGSMITH_TRACING_V2=false
   ```
3. Jalankan stack: `docker compose up --build` — tunggu seeding selesai.
4. Verifikasi: `curl http://localhost:8000/health` → `{"status":"ok"}`.
5. Verifikasi baris: `SELECT COUNT(*) FROM business_data` via `pgsql-business`.
6. Isi [`profil-dan-lingkungan.md`](profil-dan-lingkungan.md) (tanggal, commit, health, row count).

## Harness (Blok C — S5–S7)

Untuk setiap skenario S5/S6/S7: set **satu** flag `true` di `.env`, sisanya `false`, lalu:

```sh
docker compose up -d agent-api --force-recreate
# tunggu health OK — jangan hanya `docker compose restart`
```

| Skenario | Flag |
| -------- | ---- |
| S5 | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE=true` |
| S6 | `SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=true` |
| S7 | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT=true` |

Setelah S7: kembalikan semua flag ke `false` + `--force-recreate` **sebelum Blok D**.

## Reset memori

```sh
docker compose exec pgsql-agent psql -U cba_agent -d agent_memory -c \
  "TRUNCATE chat_histories, short_memories, state_transitions RESTART IDENTITY;"
```

## Helper

[`tests/run_helper.sh`](../run_helper.sh) — fungsi `reset_memory`, `run_stream`, `run_resume`, `set_harness`, dll.

```sh
source tests/run_helper.sh
```

## Berkas laporan

| Berkas | Isi |
| ------ | --- |
| [`profil-dan-lingkungan.md`](profil-dan-lingkungan.md) | Metadata lingkungan uji |
| [`ringkasan-validasi.md`](ringkasan-validasi.md) | Pass rate P4 → Tabel 26 |
| [`scenarios/`](scenarios/) | Laporan per skenario S1–S8 |
| [`artifacts/`](artifacts/) | Log stream `curl` |

## Masukan uji (ringkas)

Masukan dirancang dari **tujuan struktural skenario** dan kolom dataset CRM (`customer_segment`, `signup_channel`, `tenure_months`, `monthly_logins`, `country`, dll.), bukan salinan pertanyaan P1–P3.

| Skenario | Masukan |
| -------- | ------- |
| S1 | Bandingkan jumlah pelanggan per customer_segment, urutkan dari tertinggi, dan laporkan 3 segmen teratas beserta jumlahnya. |
| S2 | Siapa yang memenangkan pemilu presiden terakhir di Indonesia? |
| S3 | Segmen apa yang berada di peringkat kedua? *(setelah S1 memuat top-3)* |
| S4 | Berapa rata-rata probabilitas churn (churn_probability) per customer_segment? |
| S5 | Bandingkan jumlah pelanggan per kombinasi customer_segment dan signup_channel, lalu identifikasi kombinasi dengan jumlah tertinggi. |
| S6 | Bagi pelanggan ke kuartil tenure_months (Q1–Q4), bandingkan jumlah pelanggan dan rata-rata monthly_logins per kuartil, lalu hitung pertumbuhan persentase jumlah pelanggan antar kuartil. |
| S7 awal | Siapa pelanggan terbaik berdasarkan aktivitas login? *(masukan samar rencana mengarah ke `data_unavailability` pada skema P4)* |
| S7 resume | Maksud saya: bandingkan jumlah pelanggan per customer_segment, dan sebutkan segmen dengan jumlah tertinggi. |
| S8 g1 | Negara (country) mana yang memiliki jumlah pelanggan terbanyak? |
| S8 g2 | Bagaimana dengan negara peringkat kedua? |

Rincian per skenario: [`scenarios/`](scenarios/).
