# Cara kerja TF-IDF + SVM

## 1. Pakai input yang sama

Data diambil dari keluaran pipeline Athar di [JudiScope](https://github.com/atharikputra/JudiScope), commit `d9c7feb47aeac1f2889e19c2cddc255525e358ef`. Importer mengambil enam file preparation dari commit itu dan memeriksa hash pada `config/upstream_manifest.json`. Hasil classifier Athar tidak diimpor.

Pipeline Athar menghasilkan **8.934 komentar asli bersih** dan **1.066 komentar sintetis**. Untuk menjalankan ulang preparation, gunakan commit tersebut dan jalankan notebook 01 lalu 02 di JudiScope. Repo SVM memakai ekspornya agar input kelompok tetap sama.

Sumber awal menurut tim adalah [Kaggle yaemico/judionline](https://www.kaggle.com/datasets/yaemico/judionline). Lisensi, versi sumber, dan proses anotasinya belum terkonfirmasi. Komentar sintetis adalah buatan tim, bukan komentar YouTube baru.

Teks input model adalah `komentar_processed`. Cleaning mengikuti Athar: normalisasi Unicode, lowercase, ganti URL menjadi `<url>`, hapus karakter tak terlihat, lalu rapikan spasi. Angka, simbol, dan emoji dipertahankan. Tidak ada stemming atau stopword tambahan.

ID `source_row` dipakai untuk mencocokkan pembagian data. ID, metadata, flag sintetis, dan prediksi lama tidak menjadi fitur.

## 2. Pisahkan peran data

| Bagian | Jumlah asli | Untuk apa? |
| --- | ---: | --- |
| Train | 5.360 | Melatih kandidat model |
| Validation | 1.787 | Memilih fitur dan parameter C |
| Test | 1.787 | Mengukur hasil akhir |

Pembagian mengikuti `original_split_manifest.csv`; memakai seed yang sama saja belum tentu menghasilkan anggota test yang sama.

Ada dua skenario SVM: **asli saja** dan **asli + sintetis**. Seluruh 1.066 sintetis hanya boleh masuk pelatihan. Validation dan test tetap memakai komentar asli yang sama pada kedua skenario.

## 3. Ubah teks menjadi TF-IDF

SVM membutuhkan input angka. TF-IDF memberi bobot pada kata atau potongan karakter: fitur yang sering muncul dalam satu komentar mendapat bobot TF, sedangkan fitur yang terlalu umum di banyak komentar dikurangi bobotnya oleh IDF.

Dua representasi dicoba:

- **Word 1–2 gram:** kata dan pasangan kata, misalnya `review`, `mobil`, `review mobil`.
- **Character 3–5 gram (`char_wb`):** potongan karakter di dalam batas kata; berguna untuk mengenali bagian tulisan dan variasi ejaan.

Vocabulary dan IDF hanya dipelajari dari data pelatihan. Keduanya memakai `min_df=2`, maksimum 40.000 fitur, `sublinear_tf=True`, dan normalisasi L2. Pengaturan lengkap ada di `config/experiment_config.json`.

## 4. Latih dan pilih SVM

`LinearSVC` mempelajari batas pemisah pada fitur TF-IDF. Parameter **C** mengatur besarnya penalti kesalahan pelatihan. C yang lebih besar belum tentu lebih baik pada data baru.

Dicoba `C = 0.1, 1, 10`. Dua representasi × tiga C × dua skenario menghasilkan **12 kandidat**. Setiap kandidat mendapat pipeline baru. Pilihan memakai **F1 kelas 1 pada validation**, kemudian macro-F1 jika seri. Aturan seri berikutnya ada di konfigurasi.

Parameter dipilih dan dicatat sebelum test dibuka untuk evaluasi. Setelah itu, model dilatih ulang pada **train + validation**: 7.147 asli, atau 8.213 termasuk sintetis. Test tidak dipakai untuk fit atau memilih parameter.

Pada hasil yang disertakan, kedua skenario memilih **character 3–5 gram, C=10**. Skenario pilihan validation adalah `original_only`.

## 5. Baca hasilnya

Kelas positif adalah **1**. Confusion matrix memakai baris label rujukan dan kolom prediksi, urutan `[0, 1]`.

| Istilah | Artinya |
| --- | --- |
| TP | Label 1 diprediksi 1 |
| TN | Label 0 diprediksi 0 |
| FP | Label 0 diprediksi 1 |
| FN | Label 1 diprediksi 0 |
| Accuracy | `(TP + TN) / semua komentar` |
| Precision (1) | `TP / (TP + FP)` |
| Recall (1) | `TP / (TP + FN)` |
| F1 (1) | `2TP / (2TP + FP + FN)` |
| Macro-F1 | Rata-rata F1 kelas 0 dan kelas 1 |

Pembagian nol menghasilkan 0. `decision_score` adalah margin SVM, bukan probabilitas. Koefisien fitur menunjukkan asosiasi dengan keputusan model, bukan hubungan sebab-akibat.

## Yang diserahkan untuk paper

Jalankan `python scripts/package_run.py` dari root repo. ZIP berisi semua hasil berikut:

| File | Isi |
| --- | --- |
| `test_metrics.csv` | Dua baris hasil SVM; metrik skala 0–1, confusion counts, dan waktu |
| `validation_results.csv` | Semua 12 kandidat dan skor validation |
| `test_predictions.csv` | Prediksi 1.787 test per skenario, total 3.574 baris |
| `test_errors.csv` | Semua prediksi yang berbeda dari label rujukan |
| `models/` | Dua pipeline TF-IDF + SVM tersimpan |
| `experiment_summary.json` | Konfigurasi, versi library, identitas data, dan hasil |
| Catatan JSON lainnya | Pilihan sebelum test, pemeriksaan hasil, dan hash file |

Prediksi dicocokkan lewat **`scenario` + `source_row`**. Kolom `label` adalah rujukan, `prediction` adalah keluaran model, dan `processed_text_sha256` membantu memastikan teksnya sama. Dua skenario tetap memakai 1.787 test unik, bukan 3.574 observasi independen.

Untuk membandingkan dengan anggota lain, penulis paper perlu memastikan input, label, anggota test, dan definisi metrik sama. Waktu fit mencakup TF-IDF + SVM; waktu prediksi diukur terpisah. Waktu dari komputer atau versi library berbeda bukan benchmark kecepatan yang terkontrol.

Model asli saja menghasilkan **TN=1.201, FP=2, FN=20, TP=564**. Dengan sintetis, FP bertambah menjadi 3; hitungan lain tetap. Perbedaan ini hanya deskriptif pada satu split. Label belum diaudit sepenuhnya, dan template atau kampanye mirip mungkin muncul di beberapa bagian data. Generalisasi ke video/periode baru belum diukur.
