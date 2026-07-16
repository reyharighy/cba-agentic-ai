# S2 — Permintaan Luar Domain

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P3 — E-commerce |
| Kelompok | K2 — Percabangan defensif |
| Skenario | S2 |
| Tanggal run | 2026-07-16 |
| `turn_num` sebelum run | 1 |
| Test harness | Tidak |

## Masukan

```text
Siapa yang memenangkan pemilu presiden terakhir di Indonesia?
```

## Peristiwa stream

Jenis peristiwa: `update` (3×), `complete` (1×).

Cuplikan lengkap: [`artifacts/S2-stream.txt`](../../artifacts/S2-stream.txt)

## Jejak audit

| seq | node_name | event_type |
| --- | --------- | ---------- |
| 1 | intent_comprehension | update |
| 2 | request_classification | update |
| 3 | punt_response | update |
| 4 | `<complete>` | complete |

## Respons akhir

Permintaan ditolak — di luar cakupan kemampuan sistem analitik bisnis.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Node `punt_response` muncul | Ya |
| Tanpa pipeline analitik | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
