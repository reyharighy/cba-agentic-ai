# S8 — Memori Multi-Turn

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P3 — E-commerce |
| Kelompok | K4 — Memori multi-turn |
| Skenario | S8 |
| Tanggal run | 2026-07-16 |
| Test harness | Tidak (semua flag `false`) |

## Peristiwa stream

| Giliran | Jenis peristiwa | Berkas |
| ------- | --------------- | ------ |
| 1 | `update`, `complete` | [`S8-g1-stream.txt`](../../artifacts/S8-g1-stream.txt) |
| 2 | `update`, `complete` | [`S8-g2-stream.txt`](../../artifacts/S8-g2-stream.txt) |

## Giliran 1

| Field | Nilai |
| ----- | ----- |
| Masukan | Region mana yang mencatat total Sales tertinggi pada tahun 2023? |
| Jalur | Pipeline analitik penuh → `summarization` → `complete` |
| Hasil | **West** — 1.002.600 |

## Giliran 2

| Field | Nilai |
| ----- | ----- |
| Masukan | Bagaimana dengan wilayah peringkat kedua? |
| Jalur | `direct_response` → `summarization` → `complete` |
| Hasil | **South** — 954.257 |

## Riwayat percakapan

`GET /chat/history` memuat 2 giliran (West 2023 + South peringkat 2). Giliran 2 memanfaatkan konteks historis ranking Region dari giliran 1.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Dua giliran terpisah | Ya |
| Giliran 2 memahami konteks (peringkat kedua Region) | Ya |
| Memori tersimpan antar giliran | Ya |
| Kedua giliran berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
