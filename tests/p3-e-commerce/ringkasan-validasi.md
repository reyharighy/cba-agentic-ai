# Ringkasan Validasi — P3 (E-commerce)

| Field | Nilai |
| ----- | ----- |
| Profil | P3 — `dataset_3.csv` |
| Branch | `test/loop-correction` |
| Commit | `652f305` |
| Tanggal | 2026-07-16 |
| N per skenario | 1 |

## Hasil per skenario

| Skenario | Kelompok | Harness | Lulus struktural | Catatan |
| -------- | -------- | ------- | ---------------- | ------- |
| S1 | K1 | — | Ya | Top 3 Category 2023: Electronics, Accessories, Office |
| S2 | K2 | — | Ya | `punt_response`, tanpa memori |
| S3 | K2 | — | Ya | `direct_response`, Accessories peringkat 2 |
| S4 | K2 | — | Ya | `data_unavailability_response` (`customer_rating`) |
| S5 | K3 | retrieval retry once | Ya | Electronics+East tertinggi 2023 |
| S6 | K3 | analytical retry once | Ya | Kuartal 2023 + harness S6a |
| S7 | K3 | retrieval interrupt | Ya | `interrupt` → resume → `complete` |
| S8 | K4 | — | Ya | West (g1) + South peringkat 2 (g2); memori 2 giliran |

## Pass rate P3

**8 / 8 (100%)** — semua skenario lulus penilaian struktural.

## Harness

Semua flag dikembalikan ke `false`; container `agent-api` di-recreate setelah perubahan `.env`.

## Artefak

| Skenario | Berkas stream |
| -------- | ------------- |
| S1–S5 | `S1-stream.txt` … `S5-stream.txt` |
| S6 | `S6-stream.txt` |
| S7 | `S7-stream.txt`, `S7-resume-stream.txt` |
| S8 | `S8-g1-stream.txt`, `S8-g2-stream.txt` |

Indeks lengkap: [`artifacts/README.md`](artifacts/README.md)

Salin baris ini ke **Tabel 25** pada skripsi setelah pengujian selesai.
