# S8 — Memori Multi-Turn

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P2 — Penjualan kendaraan |
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
| Masukan | Negara bagian (state) mana yang mencatat total sellingprice penjualan kendaraan tertinggi pada tahun 2014? |
| Jalur | Pipeline analitik penuh → `summarization` → `complete` |
| Hasil | **FL** (Florida) — 268.977.775,0 |

## Giliran 2

| Field | Nilai |
| ----- | ----- |
| Masukan | Bagaimana dengan negara bagian peringkat kedua? |
| Jalur | Pipeline analitik penuh → `summarization` → `complete` |
| Hasil | **CA** (California) — 182.923.683,0 |

## Riwayat percakapan

`GET /chat/history` memuat 2 giliran (FL 2014 + CA peringkat 2). Giliran 2 memicu analitik baru dengan konteks historis (referensi ranking state dari giliran 1).

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Dua giliran analitik terpisah | Ya |
| Giliran 2 memahami konteks (peringkat kedua state) | Ya |
| Memori tersimpan antar giliran | Ya |
| Kedua giliran berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
