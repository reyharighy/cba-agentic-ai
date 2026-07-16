# Ringkasan Validasi — P5 (Chocolate Sales)

| Field | Nilai |
| ----- | ----- |
| Profil | P5 — `dataset_5.csv` |
| Branch | `test/loop-correction` |
| Commit | `1e9d9f7` |
| Tanggal | 2026-07-16 |
| N per skenario | 1 |

## Hasil per skenario

| Skenario | Kelompok | Harness | Lulus struktural | Catatan |
| -------- | -------- | ------- | ---------------- | ------- |
| S1 | K1 | — | Ya | Top 3 product: 50% Dark Bites, Smooth Sliky Salty, Eclairs |
| S2 | K2 | — | Ya | `punt_response`, tanpa memori |
| S3 | K2 | — | Ya | `direct_response`, Smooth Sliky Salty peringkat 2 |
| S4 | K2 | — | Ya | `data_unavailability_response` (`profit_margin`) |
| S5 | K3 | retrieval retry once | Ya | 50% Dark Bites + Australia tertinggi (16) |
| S6 | K3 | analytical retry once | Ya | Kuartil boxes_shipped; masukan disesuaikan |
| S7 | K3 | retrieval interrupt | Ya | `interrupt` → resume → `complete` |
| S8 | K4 | — | Ya | Australia (g1) + India peringkat 2 (g2); memori 2 giliran |

## Pass rate P5

**8 / 8 (100%)** — semua skenario lulus penilaian struktural.

## Agregat lintas profil (P1–P5)

| Metrik | Nilai |
| ------ | ----- |
| Kombinasi profil–skenario | 40 (5 profil × 8 skenario) |
| Pass rate agregat | 40 / 40 (100%) |

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
