# Laporan Pengujian Lintas Profil

Folder ini menyimpan hasil pengujian skenario S1–S8 per profil data bisnis (P1–P4).
Berkas di sini **dapat di-commit** ke Git (berbeda dari `.docs/` yang diabaikan).

## Pemetaan profil dan dataset

| Profil | Folder laporan | `EXTERNAL_DATASET` | File CSV | Domain |
| ------ | -------------- | ------------------ | -------- | ------ |
| **P1** | [`p1-ritel-kopi/`](p1-ritel-kopi/) | `1` | `dataset_1.csv` | Ritel kopi (referensi) |
| **P2** | [`p2-penjualan-kendaraan/`](p2-penjualan-kendaraan/) | `2` | `dataset_2.csv` | Penjualan kendaraan |
| P3 | `p3-e-commerce/` *(rencana)* | `3` | `dataset_3.csv` | E-commerce |
| P4 | `p4-crm/` *(rencana)* | `4` | `dataset_4.csv` | CRM / churn |

Rincian seeding: [`docker_script/datasets/DATASETS.md`](../docker_script/datasets/DATASETS.md).

## Urutan pelaksanaan (semua profil)

| Blok | Skenario | Reset memori |
| ---- | -------- | ------------ |
| A | S1 → S2 → S3 | Reset sebelum S1; jangan reset antara S1–S3 |
| B | S4 | Reset |
| C | S5 → S6 → S7 | Reset tiap skenario; satu flag harness aktif |
| D | S8 | Reset sebelum giliran 1 |

Panduan operasional: [`.docs/markdowns/panduan-pelaksanaan-skenario-uji.md`](../.docs/markdowns/panduan-pelaksanaan-skenario-uji.md) *(lokal, tidak di-commit)*.

## Tujuan laporan per profil

| Profil | Tujuan | Output skripsi |
| ------ | ------ | -------------- |
| P1 | Dokumentasi rinci referensi | Subbab 5.3, Tabel 15–22 |
| P2–P4 | Uji generalitas struktural | Tabel 24–26 |
| Agregat | Ringkasan lintas profil | Tabel 27 |
