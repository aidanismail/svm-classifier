# Kontrak hasil untuk anggota penulis paper

Schema version: **1.0**. Metode: **SVM**, classifier **LinearSVC**. Repo menghasilkan dua skenario SVM dan tidak menghitung perbandingan lintas-metode.

## Identitas yang harus cocok

Gunakan `config/upstream_manifest.json` untuk memeriksa commit sumber, SHA-256 data, dan hash manifest. Dataset asli bersih, label, membership test, dan tambahan sintetis harus sama pada deliverable anggota lain. Seed saja tidak cukup untuk membuktikan membership yang sama.

Label kerja `0=nonjudi`, `1=promosi judi`. Train/validation/test asli berjumlah 5.360/1.787/1.787. Test berisi 1.203 label 0 dan 584 label 1. Sintetis berjumlah 1.066, hanya untuk fitting. Final fit 7.147 record (`original_only`) atau 8.213 (`with_synthetic`). Metadata, flag, ID, dan prediksi lama tidak menjadi fitur.

## test_metrics.csv

Tepat **2 baris**, satu per skenario:

| Kolom | Makna |
| --- | --- |
| `run_id` | Identitas seluruh artefak run |
| `method`, `classifier` | `SVM`, `LinearSVC` |
| `scenario` | `original_only` atau `with_synthetic` |
| `features`, `C` | Representasi dan C hasil pemilihan validation |
| `fit_rows`, `test_rows` | Jumlah final refit dan test |
| `accuracy`, `precision_1`, `recall_1`, `f1_1`, `macro_f1` | Skala 0–1; kelas positif 1 |
| `tn`, `fp`, `fn`, `tp` | Confusion counts; label order `[0,1]` |
| `refit_seconds` | Fit TF-IDF + SVM pada development |
| `test_predict_seconds` | `Pipeline.predict` pada test; bukan total ekstraksi margin tambahan |

Ambil angka tepat dari CSV, bukan menyalin angka grafik yang sudah dibulatkan. Jika memakai persen, kalikan 100 satu kali. Macro-F1 adalah rata-rata F1 kelas, bukan F1 positif atau weighted-F1.

## test_predictions.csv

Format **long**, 1.787 record per skenario, **3.574 baris total**. Ini tetap 1.787 test unik yang dievaluasi dua kali, bukan 3.574 komentar test independen.

Kunci unik: `(run_id, scenario, source_row)`. Kolom lainnya:

- `method='SVM'`, `split='test'`.
- `label`: label rujukan canonical.
- `prediction`: prediksi 0/1.
- `decision_score`: margin SVM; **bukan probabilitas**.
- `processed_text_sha256`: SHA-256 dari byte UTF-8 `komentar_processed`, tanpa perubahan spasi/normalisasi tambahan.

Untuk mengambil teks, cocokkan `source_row` ke `data/athar/komentar_cleaned.csv`. Bandingkan membership dan label dengan keluaran anggota lain melalui ID, bukan nomor urut CSV. Jangan membandingkan besarnya margin SVM dengan probabilitas classifier lain sebagai skala keyakinan yang setara.

## Artefak pendukung

- `validation_results.csv`: seluruh 12 kandidat dengan skor validation, ukuran fit/fitur, iterasi, durasi, status konvergensi, dan peringatan.
- `selection_locked.json`: parameter dan skenario yang dipilih sebelum evaluasi test, hash CSV validation, konfigurasi, dan input.
- `classification_reports.json`: precision/recall/F1/support per kelas dan agregat.
- `test_errors.csv`: seluruh mismatch kedua skenario, teks, ID, skor, serta `false_positive` / `false_negative`.
- `selected_model_feature_weights.csv`: nama fitur dan koefisien model skenario pilihan validation.
- `experiment_summary.json`: konfigurasi, provenance, environment aktual, timing definitions, matriks, dan keterbatasan.
- `verification.json`: pemeriksaan konkret yang sudah dijalankan serta status mode kernel.
- `artifact_manifest.json`: nama/path, ukuran byte, dan SHA-256 artefak run selain manifest itu sendiri.
- `models/*.joblib`: kedua pipeline final tanpa fit pada test; masukan pipeline adalah teks yang sudah dibersihkan.

## Cara memeriksa dan menyerahkan

Jalankan `python scripts/verify_run.py --run outputs/runs/<run_id>`. Verifier memakai prediksi ekspor untuk menghitung ulang rumus metrik dan mengecek kedua model. Opsi `--skip-models` hanya memeriksa tabel; jangan melaporkannya sebagai verifikasi model lengkap.

Jalankan `python scripts/package_run.py --run outputs/runs/<run_id>` untuk membuat ZIP lokal. Bundle memuat kode, notebook, dokumentasi, snapshot input, model, prediksi, dan bukti. `BUNDLE_MANIFEST.json` berisi hash setiap entry selain manifest itu sendiri; setiap entry diperiksa saat packaging. Serahkan ZIP itu kepada anggota penulis paper secara terpisah; file rincinya sengaja tidak semua masuk Git.

Anggota keempat mengerjakan interpretasi lintas-metode dan paper. Ia perlu menyebut representasi terpilih, anggaran tuning, versi library, kondisi timing, keterbatasan label/split, dan fakta bahwa sintetis bukan data observasi baru. Bukti repo ini tidak mengesahkan implementasi anggota lain secara otomatis.
