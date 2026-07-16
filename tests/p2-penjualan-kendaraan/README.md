# P2 — Penjualan Kendaraan

Laporan pengujian skenario S1–S8 pada profil **P2** (`dataset_2.csv`, domain penjualan kendaraan lelang).

## Lingkungan

| Item | Nilai |
| ---- | ----- |
| `EXTERNAL_DATASET` | `2` |
| CSV | `docker_script/datasets/dataset_2.csv` |
| Tabel | `business_data` (default) |
| Branch uji | `test/loop-correction` |

## Pre-flight (sebelum eksekusi)

1. Pastikan `dataset_2.csv` ada secara lokal (~558k baris; seeding lebih lama dari P1).
2. Set di `.env`:
   ```env
   EXTERNAL_DATASET=2
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

Setelah S7: kembalikan semua flag ke `false` + `--force-recreate`.

## Reset memori

```sh
docker compose exec pgsql-agent psql -U cba_agent -d agent_memory -c \
  "TRUNCATE chat_histories, short_memories, state_transitions RESTART IDENTITY;"
```

## Helper

[`tests/run_helper.sh`](../run_helper.sh) — fungsi `reset_memory`, `run_stream`, `run_resume`, `set_harness`, dll. (Bersama untuk semua profil P1–P4.)

```sh
source tests/run_helper.sh
```

## Berkas laporan

| Berkas | Isi |
| ------ | --- |
| [`profil-dan-lingkungan.md`](profil-dan-lingkungan.md) | Metadata lingkungan uji |
| [`ringkasan-validasi.md`](ringkasan-validasi.md) | Pass rate P2 → Tabel 24 |
| [`scenarios/`](scenarios/) | Laporan per skenario S1–S8 |
| [`artifacts/`](artifacts/) | Log stream `curl` |

## Masukan uji (ringkas)

Masukan dirancang dari **tujuan struktural skenario** dan kolom dataset kendaraan (`make`, `body`, `state`, `sellingprice`, `saledate`, `year`), bukan salinan pertanyaan P1.

| Skenario | Masukan |
| -------- | ------- |
| S1 | Pada tahun 2014, bandingkan total sellingprice per merek (make), urutkan dari tertinggi, dan laporkan 3 merek teratas beserta nilainya. |
| S2 | Siapa yang memenangkan pemilu presiden terakhir di Indonesia? |
| S3 | Merek apa yang berada di peringkat kedua? *(setelah S1 memuat top-3)* |
| S4 | Berapa rata-rata skor kepuasan pelanggan (customer_satisfaction) per merek kendaraan? |
| S5 | Bandingkan total sellingprice penjualan kendaraan per kombinasi body dan state pada tahun 2014, lalu identifikasi kombinasi dengan performa tertinggi. |
| S6 | Pada tahun 2014, bandingkan total sellingprice dan jumlah transaksi per kuartal (Q1–Q4), lalu hitung pertumbuhan persentase revenue antar kuartal. |
| S7 awal | Bagaimana performa penjualan kendaraan terbaik untuk periode yang relevan? |
| S7 resume | Maksud saya: bandingkan total sellingprice per merek (make) pada tahun 2014, dan sebutkan merek dengan nilai tertinggi. |
| S8 g1 | Negara bagian (state) mana yang mencatat total sellingprice penjualan kendaraan tertinggi pada tahun 2014? |
| S8 g2 | Bagaimana dengan negara bagian peringkat kedua? |

Rincian per skenario: [`scenarios/`](scenarios/).
