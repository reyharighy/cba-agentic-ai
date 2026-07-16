# S5 — Self-Correction Pengambilan Data

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P1 — Ritel kopi |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S5 |
| Tanggal run | 2026-07-16 |
| `thread_id` | `cb9ad4f0-16c3-4d9d-a43e-5b7217ef3fbb` |
| Test harness | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE=true` |

## Masukan

```text
Bandingkan total net price penjualan kopi per kombinasi jenis pembayaran dan jam transaksi pada bulan Januari, lalu identifikasi kombinasi dengan performa tertinggi.
```

## Jejak audit

| seq | node_name |
| --- | --------- |
| 6–8 | data_retrieval_plan → execution → observation (siklus 1, harness: insufficient) |
| 9–11 | data_retrieval_plan → execution → observation (siklus 2, sufficient) |
| 12–17 | analytical_plan → … → `<complete>` |

Cuplikan harness: `rationale: "[scenario test] Forced insufficient observation to verify retrieval correction loop."`

Artefak: [`artifacts/S5-stream.txt`](../../artifacts/S5-stream.txt)

## Respons akhir

Kombinasi tertinggi: **card** + jam **16** — total net_price **682.36**.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Loop `data_retrieval_plan` ↔ `observation` (≥2 siklus) | Ya |
| Harness terdeteksi pada observasi pertama | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
