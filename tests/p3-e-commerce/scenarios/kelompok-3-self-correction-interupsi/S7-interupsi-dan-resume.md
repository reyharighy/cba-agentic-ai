# S7 — Interupsi dan Resume

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P3 — E-commerce |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S7 |
| Blok pelaksanaan | C (reset memori; harness S7 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT=true` |
| Tanggal run | 2026-07-16 |

## Masukan awal

```text
Bagaimana performa penjualan e-commerce terbaik untuk periode yang relevan?
```

## Masukan resume

```text
Maksud saya: bandingkan total Sales per Category pada tahun 2023, dan sebutkan kategori dengan nilai tertinggi.
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

Pipeline selesai (`complete`). Konten respons menjelaskan keterbatasan agregasi per kategori pada dataframe resume (variasi LLM); penilaian struktural fokus pada alur interrupt → resume.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Peristiwa `interrupt` pada stream awal | Ya |
| Harness memicu kegagalan retrieval berulang | Ya |
| Resume berhasil | Ya |
| Alur resume berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
