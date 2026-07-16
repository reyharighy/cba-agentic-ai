# S8 — Memori Multi-Turn

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P5 — Chocolate sales |
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
| Masukan | Negara (country) mana yang memiliki jumlah transaksi terbanyak? |
| Jalur | Pipeline analitik penuh → `summarization` → `complete` |
| Hasil | **Australia** — 205 transaksi |

## Giliran 2

| Field | Nilai |
| ----- | ----- |
| Masukan | Bagaimana dengan negara peringkat kedua? |
| Jalur | Pipeline analitik penuh → `summarization` → `complete` |
| Hasil | **India** — 184 transaksi |

## Riwayat percakapan

`GET /chat/history` memuat 2 giliran (Australia tertinggi + India peringkat 2). Giliran 2 memicu analitik baru dengan konteks historis ranking country dari giliran 1.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Dua giliran analitik terpisah | Ya |
| Giliran 2 memahami konteks (peringkat kedua country) | Ya |
| Memori tersimpan antar giliran | Ya |
| Kedua giliran berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
