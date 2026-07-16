# S5 — Self-Correction Pengambilan Data

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P2 — Penjualan kendaraan |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S5 |
| Blok pelaksanaan | C (reset memori; harness S5 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE=true` |
| Tanggal run | 2026-07-16 |

## Masukan

```text
Bandingkan total sellingprice penjualan kendaraan per kombinasi body dan state pada tahun 2014, lalu identifikasi kombinasi dengan performa tertinggi.
```

## Peristiwa stream

Jenis peristiwa: `update` (16×), `complete` (1×).

Cuplikan harness: `rationale: "[scenario test] Forced insufficient observation to verify retrieval correction loop."`

Artefak: [`artifacts/S5-stream.txt`](../../artifacts/S5-stream.txt)

## Jejak audit

| seq | node_name |
| --- | --------- |
| 6–8 | data_retrieval_plan → execution → observation (siklus 1, harness: insufficient) |
| 9–11 | data_retrieval_plan → execution → observation (siklus 2, sufficient) |
| 12–17 | analytical_plan → … → `<complete>` |

## Respons akhir

Kombinasi tertinggi: **Sedan** + **FL** (Florida) — total sellingprice **92.944.248,0**.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Loop `data_retrieval_plan` ↔ `observation` (≥2 siklus) | Ya |
| Harness terdeteksi pada observasi pertama | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
