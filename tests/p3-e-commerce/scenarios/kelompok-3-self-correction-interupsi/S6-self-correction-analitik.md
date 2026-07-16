# S6 — Self-Correction Analitik

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P3 — E-commerce |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S6 |
| Blok pelaksanaan | C (reset memori; harness S6 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=true` |
| Tanggal run | 2026-07-16 |

## Masukan

```text
Pada tahun 2023, bandingkan total Sales dan jumlah transaksi per kuartal (Q1–Q4), lalu hitung pertumbuhan persentase revenue antar kuartal.
```

## Peristiwa stream

Jenis peristiwa: `update` (16×), `complete` (1×).

Cuplikan harness: `rationale: "[scenario test] Forced insufficient observation to verify analytical correction loop."`

Artefak: [`artifacts/S6-stream.txt`](../../artifacts/S6-stream.txt)

## Jejak audit (ringkas)

| seq | node_name |
| --- | --------- |
| 9–12 | analytical_plan → execution → observation (harness: insufficient) |
| 13–16 | analytical_plan → execution → observation (sufficient) |
| 17–19 | analytical_response → summarization → `<complete>` |

## Respons akhir

Tabel Sales dan jumlah transaksi per kuartal 2023 beserta pertumbuhan persentase antar kuartal (Q3 tertinggi: 1.012.635).

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| `analytical_plan_execution` ≥ 2 kali | Ya |
| Loop `analytical_plan` ↔ `observation` (≥2) | Ya |
| Harness terdeteksi | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
