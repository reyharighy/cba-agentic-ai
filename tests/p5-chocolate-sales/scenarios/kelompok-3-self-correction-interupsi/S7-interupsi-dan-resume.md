# S7 — Interupsi dan Resume

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P5 — Chocolate sales |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S7 |
| Blok pelaksanaan | C (reset memori; harness S7 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT=true` |
| Tanggal run | 2026-07-16 |

## Masukan awal

```text
Bagaimana performa penjualan cokelat terbaik untuk periode yang relevan?
```

## Masukan resume

```text
Maksud saya: bandingkan total boxes_shipped per product pada tahun 2022, dan sebutkan produk dengan nilai tertinggi.
```

## Peristiwa stream

| Fase | Jenis peristiwa | Berkas |
| ---- | --------------- | ------ |
| Awal | `update`, `interrupt` | [`S7-stream.txt`](../../artifacts/S7-stream.txt) |
| Resume | `update`, `complete` | [`S7-resume-stream.txt`](../../artifacts/S7-resume-stream.txt) |

## Jejak audit (ringkas)

- Fase awal: loop `data_retrieval_plan` ↔ `observation` (3× harness) → `interrupt`.
- Fase resume: pipeline analitik → `summarization` → `complete`.

## Respons akhir (setelah resume)

**50% Dark Bites** — produk dengan total boxes_shipped tertinggi pada 2022.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Peristiwa `interrupt` pada stream awal | Ya |
| Harness memicu kegagalan retrieval berulang | Ya |
| Resume berhasil | Ya |
| Alur resume berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
