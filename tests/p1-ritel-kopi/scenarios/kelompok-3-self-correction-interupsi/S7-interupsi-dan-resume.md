# S7 — Interupsi dan Resume

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P1 — Ritel kopi |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S7 |
| Tanggal run | 2026-07-16 |
| Test harness | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_INTERRUPT=true` |

## Masukan awal

```text
Bagaimana performa penjualan kopi terbaik untuk periode yang relevan?
```

## Masukan resume

```text
Maksud saya: bandingkan total net price per varian kopi (coffee_name) pada bulan Januari, dan sebutkan varian dengan nilai tertinggi.
```

## Peristiwa stream

| Fase | Jenis peristiwa | Berkas |
| ---- | --------------- | ------ |
| Awal | `update`, `interrupt` | [`S7-stream.txt`](../../artifacts/S7-stream.txt) |
| Resume | `update`, `complete` | [`S7-resume-stream.txt`](../../artifacts/S7-resume-stream.txt) |

- Awal: `interrupt` setelah 3× forced insufficient retrieval observation (harness).
- Resume: `complete`.

## Jejak audit (ringkas)

- Fase awal: loop `data_retrieval_plan` ↔ `observation` (3× harness) → `data_availability` **interrupt**.
- Fase resume: pipeline analitik penuh → `summarization` → `<complete>`.

## Respons akhir (setelah resume)

Varian tertinggi Januari: **Americano with Milk** (total net_price **1604.72**).

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Peristiwa `interrupt` pada stream awal | Ya |
| Harness memicu kegagalan retrieval berulang | Ya |
| Resume berhasil | Ya |
| Alur resume berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
