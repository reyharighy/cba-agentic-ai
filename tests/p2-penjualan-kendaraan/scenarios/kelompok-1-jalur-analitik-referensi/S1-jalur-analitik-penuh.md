# S1 — Jalur Analitik Penuh

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P2 — Penjualan kendaraan |
| Kelompok | K1 — Jalur analitik referensi |
| Skenario | S1 |
| Tanggal run | 2026-07-16 |
| `turn_num` sebelum run | 0 |
| Test harness | Tidak |

## Masukan

```text
Pada tahun 2014, bandingkan total sellingprice per merek (make), urutkan dari tertinggi, dan laporkan 3 merek teratas beserta nilainya.
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

| Peringkat | Merek | Total sellingprice |
| --------- | ----- | ------------------ |
| 1 | **Ford** | 381.516.054 |
| 2 | **Chevrolet** | 171.767.385 |
| 3 | **Dodge** | 119.831.140 |

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Alur berakhir `complete` | Ya |
| Node `summarization` sebelum `<complete>` | Ya |
| Pipeline penuh | Ya |
| Respons analitik relevan | Ya |
| **Lulus struktural** | **Ya** |
