# S1 — Jalur Analitik Penuh

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P4 — CRM / churn |
| Kelompok | K1 — Jalur analitik referensi |
| Skenario | S1 |
| Tanggal run | 2026-07-16 |
| `turn_num` sebelum run | 0 |
| Test harness | Tidak |

## Masukan

```text
Bandingkan jumlah pelanggan per customer_segment, urutkan dari tertinggi, dan laporkan 3 segmen teratas beserta jumlahnya.
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

| Peringkat | Segment | Jumlah pelanggan |
| --------- | ------- | ---------------- |
| 1 | **Individual** | 5.984 |
| 2 | **SME** | 3.029 |
| 3 | **Enterprise** | 987 |

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Alur berakhir `complete` | Ya |
| Node `summarization` sebelum `<complete>` | Ya |
| Pipeline penuh (intent → retrieval → analitik → respons) | Ya |
| Respons analitik relevan dengan masukan | Ya |
| **Lulus struktural** | **Ya** |
