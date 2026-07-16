# Ringkasan Validasi — P2 (Penjualan Kendaraan)

| Field | Nilai |
| ----- | ----- |
| Profil | P2 — `dataset_2.csv` |
| Branch | `test/loop-correction` |
| Commit | `2e2fe69` |
| Tanggal | 2026-07-16 |
| N per skenario | 1 |

## Hasil per skenario

| Skenario | Kelompok | Harness | Lulus struktural | Catatan |
| -------- | -------- | ------- | ---------------- | ------- |
| S1 | K1 | — | Ya | Top 3 merek 2014: Ford, Chevrolet, Dodge |
| S2 | K2 | — | Ya | `punt_response`, tanpa memori |
| S3 | K2 | — | Ya | `direct_response`, Chevrolet peringkat 2 |
| S4 | K2 | — | Ya | `data_unavailability_response` (`customer_satisfaction`) |
| S5 | K3 | retrieval retry once | Ya | Sedan+FL tertinggi 2014 |
| S6 | K3 | analytical retry once | Ya | Kuartal 2014 + harness S6a |
| S7 | K3 | retrieval interrupt | Ya | `interrupt` → resume → `complete` |
| S8 | K4 | — | Ya | FL (g1) + CA peringkat 2 (g2); memori 2 giliran |

## Pass rate P2

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

Salin baris ini ke **Tabel 24** pada skripsi setelah pengujian selesai.
