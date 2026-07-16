# P5 — Chocolate Sales

Laporan pengujian skenario S1–S8 pada profil **P5** (`dataset_5.csv`, domain penjualan cokelat).

## Lingkungan

| Item | Nilai |
| ---- | ----- |
| `EXTERNAL_DATASET` | `5` |
| CSV | `docker_script/datasets/dataset_5.csv` |
| Tabel | `business_data` (default) |
| Branch uji | `test/loop-correction` |

## Pre-flight (sebelum eksekusi)

1. Pastikan `dataset_5.csv` ada secara lokal (~1.094 baris).
2. Set di `.env`:
   ```env
   EXTERNAL_DATASET=5
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
| [`ringkasan-validasi.md`](ringkasan-validasi.md) | Pass rate P5 |
| [`scenarios/`](scenarios/) | Laporan per skenario S1–S8 |
| [`artifacts/`](artifacts/) | Log stream `curl` |

## Masukan uji (ringkas)

Masukan dirancang dari **tujuan struktural skenario** dan kolom dataset P5 (`product`, `country`, `sales_person`, `date`, `boxes_shipped`, dll.), bukan salinan pertanyaan P1–P4.

| Skenario | Masukan |
| -------- | ------- |
| S1 | Pada tahun 2022, bandingkan total boxes_shipped per product, urutkan dari tertinggi, dan laporkan 3 produk teratas beserta jumlahnya. |
| S2 | Siapa yang memenangkan pemilu presiden terakhir di Indonesia? |
| S3 | Produk apa yang berada di peringkat kedua? *(setelah S1 memuat top-3)* |
| S4 | Berapa rata-rata profit_margin per product? |
| S5 | Bandingkan jumlah transaksi per kombinasi product dan country, lalu identifikasi kombinasi dengan jumlah tertinggi. |
| S6 | Bagi transaksi ke empat kuartil berdasarkan nilai boxes_shipped (Q1–Q4), lalu bandingkan jumlah transaksi dan rata-rata boxes_shipped per kuartil. *(kuartil kalender 2022 mengarah ke `data_unavailability` karena data hanya Jan–Agu 2022)* |
| S7 awal | Bagaimana performa penjualan cokelat terbaik untuk periode yang relevan? |
| S7 resume | Maksud saya: bandingkan total boxes_shipped per product pada tahun 2022, dan sebutkan produk dengan nilai tertinggi. |
| S8 g1 | Negara (country) mana yang memiliki jumlah transaksi terbanyak? |
| S8 g2 | Bagaimana dengan negara peringkat kedua? |

Rincian per skenario: [`scenarios/`](scenarios/).
