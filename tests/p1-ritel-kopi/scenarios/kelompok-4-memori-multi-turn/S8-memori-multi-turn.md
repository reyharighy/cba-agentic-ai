# S8 — Memori Multi-Turn

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P1 — Ritel kopi |
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
| Masukan | Produk kopi apa yang paling laris pada bulan Januari berdasarkan total net price? |
| `thread_id` | `7e035e58-c6f6-4558-86f6-043e6b1b4773` |
| Jalur | Pipeline analitik penuh → `summarization` → `complete` |
| Hasil | **Americano with Milk** — 1604.72 |

## Giliran 2

| Field | Nilai |
| ----- | ----- |
| Masukan | Bagaimana dengan bulan sebelumnya? |
| `thread_id` | `6ef30709-c44b-4db6-a184-98b4f8e05dda` |
| Jalur | Pipeline analitik penuh (Desember) → `summarization` → `complete` |
| Hasil | **Americano with Milk** — 1759.02 (Desember) |

## Riwayat percakapan

`GET /chat/history` memuat 2 giliran (Januari + Desember). Giliran 2 memicu analitik baru dengan konteks historis (referensi periode sebelumnya).

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Dua giliran analitik terpisah | Ya |
| Giliran 2 memahami konteks (bulan sebelumnya = Desember) | Ya |
| Memori tersimpan antar giliran | Ya |
| Kedua giliran berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
