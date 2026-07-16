# S6 — Self-Correction Analitik

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P1 — Ritel kopi |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S6 |
| Tanggal run | 2026-07-16 |
| `thread_id` | `6990025b-e24e-4d06-8cb9-c0c14c6db6bd` |
| Test harness | `SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=true` |

## Masukan

```text
Pada bulan Januari, bandingkan total net price penjualan per hari (day_name) dan identifikasi hari dengan omzet tertinggi.
```

## Jejak audit

| seq | node_name |
| --- | --------- |
| 6–8 | data_retrieval_plan → execution → observation |
| 9–10 | analytical_plan → execution (siklus 1) |
| 11 | analytical_plan_observation (harness: insufficient) |
| 12–14 | analytical_plan → execution → observation (siklus 2) |
| 15–17 | analytical_response → summarization → `<complete>` |

Cuplikan harness: `rationale: "[scenario test] Forced insufficient observation to verify analytical correction loop."`

Artefak: [`artifacts/S6-stream.txt`](../../artifacts/S6-stream.txt)

## Respons akhir

Hari dengan omzet tertinggi pada Januari: **Friday (Fri)** — total net_price **1307.90**.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| `analytical_plan_execution` ≥ 2 kali | Ya (2×) |
| Loop `analytical_plan` ↔ `observation` (≥2) | Ya |
| Harness terdeteksi | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
