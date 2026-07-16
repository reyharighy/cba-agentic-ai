# Ringkasan Validasi — P1 (Ritel Kopi)

| Field | Nilai |
| ----- | ----- |
| Profil | P1 — `dataset_1.csv` |
| Branch | `test/loop-correction` |
| Commit | `6870cda` |
| Tanggal | 2026-07-16 |
| N per skenario | 1 |

## Hasil per skenario

| Skenario | Kelompok | Harness | Lulus struktural | Catatan |
| -------- | -------- | ------- | ---------------- | ------- |
| S1 | K1 | — | Ya | Pipeline penuh, Americano with Milk |
| S2 | K2 | — | Ya | `punt_response`, tanpa memori |
| S3 | K2 | — | Ya | `direct_response`, Latte peringkat 2 |
| S4 | K2 | — | Ya | `data_unavailability_response` (teh) |
| S5 | K3 | retrieval retry once | Ya | Loop plan↔observation terverifikasi |
| S6 | K3 | analytical retry once | Ya | Omzet per day_name Januari; Fri tertinggi |
| S7 | K3 | retrieval interrupt | Ya | Interrupt → resume → complete |
| S8 | K4 | — | Ya | Januari + Desember, memori 2 giliran |

## Pass rate P1

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
