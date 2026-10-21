# Metode TF-IDF + SVM

## Gambaran untuk pembaca

Komentar berbentuk teks, sedangkan SVM bekerja dengan angka. Karena itu, **TF-IDF adalah representasi input**, sementara **SVM adalah metode klasifikasi**. Model menerima `komentar_processed` dan mengeluarkan prediksi `0` atau `1`.

Contoh alur: komentar asli diproses dengan cleaning Athar, dipotong menjadi kata/frasa atau potongan karakter, diberi bobot TF-IDF, lalu dimasukkan ke LinearSVC. Fungsi cleaning tidak memutuskan label; keputusan dipelajari classifier dari contoh fitting.

## 1. Input dan cleaning

Semua anggota menggunakan snapshot sumber yang sama. Importer mengambil keluaran pipeline Athar dari commit yang tetap dan mengecek SHA-256, sehingga perbedaan metode tidak disebabkan oleh pergantian dataset atau split secara diam-diam.

Cleaning menggunakan Unicode NFKC, menghapus karakter format tak terlihat, mengganti karakter kontrol menjadi spasi, mengubah huruf menjadi kecil, mengganti URL http/https/www dengan `<url>`, dan merapikan spasi. Angka, simbol, dan emoji dipertahankan. Tidak ada stemming atau penghapusan stopword tambahan.

`source_row` hanya ID untuk mencocokkan manifest; metadata, prediksi lama, jumlah duplikat, dan flag sintetis bukan fitur. Label kerja `0=nonjudi`, `1=promosi judi` tetap memiliki keterbatasan dokumentasi sumber.

## 2. TF-IDF: dari teks ke vektor

TF mengukur kemunculan fitur dalam satu komentar. IDF memberi bobot lebih kecil pada fitur yang muncul di banyak komentar fitting. Konfigurasi memakai `sublinear_tf=True`, yaitu frekuensi positif diganti dengan `1 + log(tf)`, serta IDF yang dihaluskan. Vektor dinormalisasi L2.

Dengan smoothing, IDF mengikuti `log((1+n)/(1+df)) + 1`, dengan `n` jumlah dokumen fitting dan `df` jumlah dokumen fitting yang mengandung fitur. Vocabulary dan nilai IDF hanya dipelajari dari bagian yang boleh digunakan untuk fit.

Dua kandidat representasi:

| Representasi | Contoh konsep | Tujuan |
| --- | --- | --- |
| Word 1–2 gram | `review`, `mobil`, `review mobil` | Menangkap kata dan frasa pendek |
| Character `char_wb` 3–5 gram | Potongan karakter di dalam batas kata | Menangkap pola tulisan dan bagian nama |

Keduanya memakai `min_df=2`, `max_features=40000`, `lowercase=False` karena teks telah dibersihkan, dan normalisasi L2. Maksimum 40.000 bukan jaminan jumlah fitur aktual tepat 40.000. Matrik TF-IDF tetap sparse agar tidak memboroskan memori.

## 3. SVM dan parameter C

`LinearSVC` mempelajari batas keputusan linear pada ruang TF-IDF. Ia menyeimbangkan margin dan penalti kesalahan. C yang lebih besar memberi penalti kesalahan fitting lebih kuat, tetapi belum tentu memberi hasil validation yang lebih baik.

Dicoba `C = 0.1, 1, 10` dengan penalti L2, `squared_hinge`, `dual='auto'`, toleransi `1e-4`, `max_iter=10000`, `class_weight=None`, dan `random_state=42`. Seluruh konfigurasi tersedia di `config/experiment_config.json`; nilai yang akhirnya dipakai ditentukan melalui validation.

Output `decision_function` adalah margin terhadap batas keputusan, bukan probabilitas. Pada urutan kelas `[0,1]`, skor positif berada pada sisi kelas `1`. Tidak dilakukan kalibrasi probabilitas atau tuning threshold. Prediksi tetap menggunakan keputusan bawaan classifier.

## 4. Train, validation, dan test

| Bagian | Peran | Original only | With synthetic |
| --- | --- | ---: | ---: |
| Train | Melatih kandidat | 5.360 asli | 6.426 termasuk 1.066 sintetis |
| Validation | Memilih fitur/C dan skenario | 1.787 asli | 1.787 asli yang sama |
| Development | Refit setelah pilihan dikunci | 7.147 asli | 8.213 termasuk sintetis |
| Test | Evaluasi akhir | 1.787 asli | 1.787 asli yang sama |

Terdapat 12 kandidat: dua representasi × tiga C × dua skenario. Skor utama seleksi adalah F1 positif, kemudian macro-F1. Pemecah seri dan preferensi skenario tertulis di konfigurasi. Hasil seleksi disimpan sebelum test. Pipeline final baru dilatih pada development; vocabulary/IDF ikut dipelajari ulang.

Kedua skenario memakai test yang identik; sintetis tidak masuk validation/test. Pembacaan manifest dengan `source_row` wajib diikuti, bukan membuat split baru dengan seed yang kebetulan sama.

## 5. Evaluasi

Confusion matrix memakai baris label rujukan dan kolom prediksi, urutan `[0,1]`:

| | Prediksi 0 | Prediksi 1 |
| --- | --- | --- |
| Label 0 | TN | FP |
| Label 1 | FN | TP |

- Accuracy = `(TP+TN)/(TP+TN+FP+FN)`.
- Precision positif = `TP/(TP+FP)`; berapa bagian prediksi promosi yang cocok dengan label positif.
- Recall positif = `TP/(TP+FN)`; berapa bagian label promosi yang terdeteksi.
- F1 positif = `2TP/(2TP+FP+FN)`.
- Macro-F1 = rata-rata F1 kelas `0` dan `1`.

Pembagian nol menghasilkan 0. Skor CSV memakai skala 0–1; tabel presentasi boleh memakai persen secara konsisten. Setiap skor dapat dihitung ulang melalui prediksi per record dan skrip verifikasi independen.

## Referensi implementasi

- [TF-IDF scikit-learn](https://scikit-learn.org/1.4/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html).
- [LinearSVC scikit-learn](https://scikit-learn.org/1.4/modules/generated/sklearn.svm.LinearSVC.html).
- [Pipeline scikit-learn](https://scikit-learn.org/1.4/modules/generated/sklearn.pipeline.Pipeline.html).

Referensi dataset dan keterbatasan anotasi harus tetap dibawa ke paper oleh anggota penulis; repo ini tidak mengisi metadata sumber yang belum diverifikasi.
