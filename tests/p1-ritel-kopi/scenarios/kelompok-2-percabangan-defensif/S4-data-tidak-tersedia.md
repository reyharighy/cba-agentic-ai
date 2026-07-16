# S4 — Data Tidak Tersedia

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P1 — Ritel kopi |
| Kelompok | K2 — Percabangan defensif |
| Skenario | S4 |
| Tanggal run | 2026-07-16 |
| `turn_num` sebelum run | 0 (reset memori) |
| `thread_id` | `d3f0b3df-454e-4497-b9ec-60eff2a5d1e8` |
| Test harness | Tidak |

## Masukan

```text
Berapa total penjualan produk teh pada tahun lalu?
```

## Peristiwa stream

Jenis peristiwa: `update` (7×), `complete` (1×).

Cuplikan lengkap: [`artifacts/S4-stream.txt`](../../artifacts/S4-stream.txt)

## Jejak audit

| seq | node_name | event_type |
| --- | --------- | ---------- |
| 1 | intent_comprehension | update |
| 2 | request_classification | update |
| 3 | context_distillation | update |
| 4 | analytical_requirement | update |
| 5 | data_availability | update |
| 6 | data_unavailability_response | update |
| 7 | summarization | update |
| 8 | `<complete>` | complete |

## Respons akhir

Sistem menjelaskan bahwa data produk teh tidak tersedia pada skema/dataset — tidak menghasilkan angka fiktif.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| `data_unavailability_response` setelah `data_availability` | Ya |
| Alur berakhir melalui `summarization` | Ya |
| Respons menjelaskan keterbatasan data | Ya |
| **Lulus struktural** | **Ya** |
