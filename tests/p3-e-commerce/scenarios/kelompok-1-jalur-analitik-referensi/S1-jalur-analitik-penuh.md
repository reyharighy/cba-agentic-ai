# S1 — Jalur Analitik Penuh

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P3 — E-commerce |
| Kelompok | K1 — Jalur analitik referensi |
| Skenario | S1 |
| Tanggal run | 2026-07-16 |
| `turn_num` sebelum run | 0 |
| Test harness | Tidak |

## Masukan

```text
Pada tahun 2023, bandingkan total Sales per Category, urutkan dari tertinggi, dan laporkan 3 kategori teratas beserta nilainya.
```

## Peristiwa stream

Jenis peristiwa: `update` (13×), `complete` (1×).

Cuplikan lengkap: [`artifacts/S1-stream.txt`](../../artifacts/S1-stream.txt)

## Jejak audit

| seq | node_name | event_type |
| --- | --------- | ---------- |
| 1–13 | intent_comprehension → … → summarization | update |
| 14 | `<complete>` | complete |

## Respons akhir

| Peringkat | Category | Total Sales |
| --------- | -------- | ----------- |
| 1 | **Electronics** | 1.881.367 |
| 2 | **Accessories** | 1.495.723 |
| 3 | **Office** | 409.502 |

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Alur berakhir `complete` | Ya |
| Node `summarization` sebelum `<complete>` | Ya |
| Pipeline penuh (intent → retrieval → analitik → respons) | Ya |
| Respons analitik relevan dengan masukan | Ya |
| **Lulus struktural** | **Ya** |
