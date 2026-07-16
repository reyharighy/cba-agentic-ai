# Artefak Stream — P3

Log keluaran `curl -N POST /agent/stream` (dan `/agent/resume` untuk S7).

| Berkas | Skenario | Keterangan |
| ------ | -------- | ---------- |
| `S1-stream.txt` | S1 | Jalur analitik penuh — top 3 Category 2023 |
| `S2-stream.txt` | S2 | Permintaan luar domain |
| `S3-stream.txt` | S3 | Respons langsung (`direct_response`) |
| `S4-stream.txt` | S4 | Data tidak tersedia (`customer_rating`) |
| `S5-stream.txt` | S5 | Self-correction retrieval (harness) |
| `S6-stream.txt` | S6 | Self-correction analitik (harness) |
| `S7-stream.txt` | S7 | Fase awal — `interrupt` |
| `S7-resume-stream.txt` | S7 | Fase resume — `complete` |
| `S8-g1-stream.txt` | S8 giliran 1 | Region tertinggi 2023 |
| `S8-g2-stream.txt` | S8 giliran 2 | Region peringkat kedua |
