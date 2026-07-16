# S6 — Self-Correction Analitik

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P2 — Penjualan kendaraan |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S6 |
| Blok pelaksanaan | C (reset memori; harness S6 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=true` |
| Tanggal run | 2026-07-16 |

## Masukan

```text
Pada tahun 2014, bandingkan total sellingprice dan jumlah transaksi per kuartal (Q1–Q4), lalu hitung pertumbuhan persentase revenue antar kuartal.
```

## Peristiwa stream

Jenis peristiwa: `update` (21×), `complete` (1×).

Cuplikan harness: `rationale: "[scenario test] Forced insufficient observation to verify analytical correction loop."`

Artefak: [`artifacts/S6-stream.txt`](../../artifacts/S6-stream.txt)

## Jejak audit (ringkas)

| seq | node_name |
| --- | --------- |
| 9–10 | analytical_plan → execution (siklus 1; error SyntaxError lalu perbaikan) |
| 11–12 | analytical_plan → execution → observation (harness: insufficient) |
| 13–14 | analytical_plan → observation (LLM insufficient, tanpa harness) |
| 15–20 | analytical_plan → execution → observation (siklus final, sufficient) |
| 21–23 | analytical_response → summarization → `<complete>` |

## Respons akhir

Tabel revenue dan jumlah transaksi per kuartal 2014 beserta pertumbuhan persentase antar kuartal.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| `analytical_plan_execution` ≥ 2 kali | Ya |
| Loop `analytical_plan` ↔ `observation` (≥2) | Ya |
| Harness terdeteksi | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
