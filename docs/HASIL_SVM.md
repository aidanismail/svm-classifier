# Hasil TF-IDF + SVM

Run yang dilaporkan: **`20261021T140045Z_c5de4779`**. Bukti numerik ada di `outputs/runs/<run_id>/`. Hasil ini hanya membahas SVM.

## Konfigurasi yang dipilih

Semua 12 kandidat selesai tanpa peringatan konvergensi. Konfigurasi terbaik pada kedua skenario adalah TF-IDF karakter `char_wb` 3–5 gram, `C=10`, dengan pengaturan tetap pada `config/experiment_config.json`.

| Skenario | F1 positif validation | Macro-F1 validation | Kandidat fit |
| --- | ---: | ---: | ---: |
| Original only | 98,5307% | 98,9137% | 6 |
| With synthetic | 98,3635% | 98,7880% | 6 |

`original_only` dipilih dari validation sebelum test. Final refit mempelajari 30.138 fitur dari 7.147 record asli untuk original-only, serta 30.294 fitur dari 8.213 record untuk augmented. Jumlah iterasi refit masing-masing 200 dan 224.

## Evaluasi test

Setiap skenario menguji **1.787 record asli yang identik**: 1.203 label `0` dan 584 label `1`.

| Skenario | Accuracy | Precision (1) | Recall (1) | F1 (1) | Macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original only | 98,7689% | 99,6466% | 96,5753% | 98,0870% | 98,5897% |
| With synthetic | 98,7129% | 99,4709% | 96,5753% | 98,0017% | 98,5263% |

| Skenario | TN | FP | FN | TP | Total salah |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original only | 1.201 | 2 | 20 | 564 | 22 |
| With synthetic | 1.200 | 3 | 20 | 564 | 23 |

Augmentasi pada run ini menambah satu false positive, sementara jumlah false negative tetap 20. F1 positif turun sekitar **0,085 poin persentase**. Ini adalah selisih deskriptif pada satu split; tidak ada klaim signifikansi statistik atau penyebab tunggal.

Precision tinggi menunjukkan sedikit prediksi positif yang tidak cocok dengan label rujukan. Recall lebih rendah daripada precision: masih ada 20 record berlabel positif yang diprediksi negatif. Accuracy tidak menggantikan pembahasan kedua jenis kesalahan tersebut.

## Contoh pembahasan kesalahan

Seluruh kesalahan disimpan dalam `test_errors.csv` untuk dua skenario, dengan ID yang bisa dicocokkan ke input asli. Pada original-only, `source_row=1838` memuat pola testimoni deposit/keuntungan namun diprediksi 0. Sebaliknya, `source_row=6726` merupakan komentar berlabel 0 yang diprediksi 1.

Beberapa false negative tampak seperti komentar umum, misalnya `source_row=6611` dengan teks “akari awetnya terbaik”. Ini memunculkan kebutuhan meninjau dokumentasi/anotasi sumber, tetapi **bukan alasan mengubah label test dan menghitung ulang skor agar meningkat**. Paper perlu membedakan prediksi yang tidak cocok dengan label rujukan dari klaim bahwa model atau anotator pasti salah.

Fitur berbobot besar termasuk potongan angka/nama dan tanda baca. Pola ini mendukung pembahasan kemungkinan shortcut dataset; koefisien tidak membuktikan hubungan sebab-akibat.

## Waktu dan lingkungan

Refit original-only sekitar 0,447 detik, augmented sekitar 0,554 detik; total fit 12 kandidat sekitar 2,807 detik pada mesin run ini. Angka tepat tersedia pada CSV/summary. Waktu mencakup fit TF-IDF dan SVM; waktu prediksi diukur terpisah dan tidak mencakup panggilan margin tambahan. Ini bukan benchmark lintas-mesin.

Sel kode sudah dieksekusi berurutan melalui IPython dan bukti numerik/model lulus pemeriksaan. Kernel Jupyter belum diverifikasi. Scientific stack berbeda dari upstream; lihat `LINGKUNGAN.md`. Hasil tidak diklaim berasal dari library upstream yang tidak tersedia.

## Batas kesimpulan

Label dan cara anotasi belum terkonfirmasi, split acak dapat memuat template/kampanye mirip di beberapa bagian, dan sintetis bukan pengamatan YouTube independen. Generalisasi ke video, periode, atau kampanye baru belum diukur. Anggota keempat menggunakan artefak SVM ini sebagai satu masukan untuk paper; perbandingan dengan metode lain tidak dilakukan di repo ini.
