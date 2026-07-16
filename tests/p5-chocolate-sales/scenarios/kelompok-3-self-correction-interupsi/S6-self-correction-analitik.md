# S6 — Self-Correction Analitik

## Metadata

| Field | Nilai |
| ----- | ----- |
| Profil | P5 — Chocolate sales |
| Kelompok | K3 — Self-correction & interupsi |
| Skenario | S6 |
| Blok pelaksanaan | C (reset memori; harness S6 aktif) |
| Test harness | `SCENARIO_TEST_FORCE_ANALYTICAL_RETRY_ONCE=true` |
| Tanggal run | 2026-07-16 |

## Masukan

```text
Bagi transaksi ke empat kuartil berdasarkan nilai boxes_shipped (Q1–Q4), lalu bandingkan jumlah transaksi dan rata-rata boxes_shipped per kuartil.
```

> Catatan: Masukan rencana awal (kuartil kalender Q1–Q4 tahun 2022) mengarah ke `data_unavailability_response` karena data hanya mencakup Jan–Agu 2022. Masukan di atas memakai kuartil distribusi `boxes_shipped` (pola serupa P4 tenure).

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

Tabel kuartil `boxes_shipped`: Q1 (276 transaksi, rata-rata 36,75) → Q4 (274 transaksi, rata-rata 334,72).

## Penilaian struktural

| Kriteria | Ya/Tidak |
| -------- | -------- |
| `analytical_plan_execution` ≥ 2 kali | Ya |
| Loop `analytical_plan` ↔ `observation` (≥2) | Ya |
| Harness terdeteksi | Ya |
| Alur berakhir `complete` | Ya |
| **Lulus struktural** | **Ya** |
