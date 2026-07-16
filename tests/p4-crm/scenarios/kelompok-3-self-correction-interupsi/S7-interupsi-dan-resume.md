# S7 — Interupsi dan Resume

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P4 — CRM / churn |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S7 |
| Blok pelaksanaan | C (reset memori; harness S7 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT=true` |
| Tanggal run | 2026-07-16 |

## Masukan awal

```text
Siapa pelanggan terbaik berdasarkan aktivitas login?
```

> Catatan: Masukan samar *"Bagaimana performa pelanggan terbaik untuk periode yang relevan?"* mengarah ke `data_unavailability_response` karena skema P4 tidak memiliki kolom tanggal/revenue. Masukan di atas memetakan aktivitas ke `monthly_logins` sambil tetap memicu loop retrieval → `interrupt`.

## Masukan resume

```text
Maksud saya: bandingkan jumlah pelanggan per customer_segment, dan sebutkan segmen dengan jumlah tertinggi.
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

Pipeline selesai (`complete`). Konten respons menjelaskan keterbatasan agregasi segment pada dataframe resume (variasi LLM); penilaian struktural fokus pada alur interrupt → resume.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Peristiwa `interrupt` pada stream awal | Ya |
| Harness memicu kegagalan retrieval berulang | Ya |
| Resume berhasil | Ya |
| Alur resume berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
