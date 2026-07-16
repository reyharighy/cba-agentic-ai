# S5 — Self-Correction Pengambilan Data

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P5 — Chocolate sales |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S5 |
| Blok pelaksanaan | C (reset memori; harness S5 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_DATA_RETRIEVAL_RETRY_ONCE=true` |
| Tanggal run | 2026-07-16 |

## Masukan

```text
Bandingkan jumlah transaksi per kombinasi product dan country, lalu identifikasi kombinasi dengan jumlah tertinggi.
```

## Peristiwa stream

Jenis peristiwa: `update` (16×), `complete` (1×).

Cuplikan harness: `rationale: "[scenario test] Forced insufficient observation to verify retrieval correction loop."`

Artefak: [`artifacts/S5-stream.txt`](../../artifacts/S5-stream.txt)

## Jejak audit (ringkas)

- Siklus 1: `data_retrieval_plan` → execution → observation (harness: insufficient).
- Siklus 2: replan → execution → observation (sufficient) → pipeline analitik → `complete`.

## Respons akhir

Kombinasi tertinggi: **50% Dark Bites + Australia** — 16 transaksi.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| Loop `data_retrieval_plan` ↔ `observation` (≥2) | Ya |
| Harness terdeteksi | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
