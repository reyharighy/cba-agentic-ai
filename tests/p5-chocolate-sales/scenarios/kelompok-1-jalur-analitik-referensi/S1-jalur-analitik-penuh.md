# S1 — Jalur Analitik Penuh

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P5 — Chocolate sales |
| Kelompok | K1 — Jalur analitik referensi |
| Skenario | S1 |
| Tanggal run | 2026-07-16 |
| `turn_num` sebelum run | 0 |
| Test harness | Tidak |

## Masukan

```text
Pada tahun 2022, bandingkan total boxes_shipped per product, urutkan dari tertinggi, dan laporkan 3 produk teratas beserta jumlahnya.
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

| Peringkat | Product | Total boxes_shipped |
| --------- | ------- | ------------------- |
| 1 | **50% Dark Bites** | 9.792 |
| 2 | **Smooth Sliky Salty** | 8.810 |
| 3 | **Eclairs** | 8.757 |

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Alur berakhir `complete` | Ya |
| Node `summarization` sebelum `<complete>` | Ya |
| Pipeline penuh (intent → retrieval → analitik → respons) | Ya |
| Respons analitik relevan dengan masukan | Ya |
| **Lulus struktural** | **Ya** |
