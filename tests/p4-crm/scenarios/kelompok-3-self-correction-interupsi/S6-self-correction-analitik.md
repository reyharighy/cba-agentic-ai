# S6 — Self-Correction Analitik

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P4 — CRM / churn |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S6 |
| Blok pelaksanaan | C (reset memori; harness S6 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=true` |
| Tanggal run | 2026-07-16 |

## Masukan

```text
Bagi pelanggan ke kuartil tenure_months (Q1–Q4), bandingkan jumlah pelanggan dan rata-rata monthly_logins per kuartil, lalu hitung pertumbuhan persentase jumlah pelanggan antar kuartil.
```

## Peristiwa stream

Jenis peristiwa: `update` (18×), `complete` (1×).

Cuplikan harness: `rationale: "[scenario test] Forced insufficient observation to verify analytical correction loop."`

Artefak: [`artifacts/S6-stream.txt`](../../artifacts/S6-stream.txt)

## Jejak audit (ringkas)

| seq | node_name |
| --- | --------- |
| 9–12 | analytical_plan → execution → observation (harness: insufficient) |
| 13–18 | analytical_plan → execution → observation (sufficient) |
| 19–21 | analytical_response → summarization → `<complete>` |

## Respons akhir

Tabel kuartil tenure_months: jumlah pelanggan, rata-rata `monthly_logins`, dan pertumbuhan persentase antar kuartil.

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| `analytical_plan_execution` ≥ 2 kali | Ya |
| Loop `analytical_plan` ↔ `observation` (≥2) | Ya |
| Harness terdeteksi | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
