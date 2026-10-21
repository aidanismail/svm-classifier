# svm-classifier

Klasifikasi komentar promosi judi online di YouTube menggunakan **TF-IDF** dan **Support Vector Machine (SVM)** dengan implementasi `LinearSVC` dari scikit-learn.

Proyek ini mencakup persiapan input, pemilihan parameter melalui validation, evaluasi test, dan ekspor model serta prediksi. Dataset dan pembagian data mengikuti pipeline [JudiScope](https://github.com/atharikputra/JudiScope).

## Metodologi

Alur eksperimen tersedia dalam [svm_experiments.ipynb](svm_experiments.ipynb), lengkap dengan kode, tabel evaluasi, dan visualisasi.

```text
Komentar bersih → TF-IDF → SVM → prediksi → evaluasi
```

TF-IDF merepresentasikan teks sebagai vektor berbobot, kemudian SVM mempelajari batas keputusan untuk klasifikasi biner. Eksperimen menguji TF-IDF kata 1–2 gram dan karakter 3–5 gram dengan `C = 0.1, 1, 10` pada dua skenario pelatihan: data asli dan data asli dengan tambahan sintetis.

Parameter dipilih berdasarkan F1 kelas positif pada validation, dengan macro-F1 sebagai pemecah seri. Model terpilih dilatih ulang pada train + validation sebelum dievaluasi pada test. Data sintetis hanya digunakan untuk pelatihan.

## Dataset

Input terdiri dari **8.934 komentar asli bersih** dan **1.066 komentar sintetis**. Pembagian komentar asli mengikuti manifest JudiScope:

| Bagian | Jumlah komentar |
| --- | ---: |
| Train | 5.360 |
| Validation | 1.787 |
| Test | 1.787 |

Importer mengambil keluaran preparation dari commit `d9c7feb47aeac1f2889e19c2cddc255525e358ef` dan memeriksa hash file sebelum digunakan. Notebook tidak membuat pembagian data baru. Identitas sumber dan file tercatat di [config/upstream_manifest.json](config/upstream_manifest.json).

## Hasil

Kedua skenario diuji pada **1.787 komentar asli yang sama**: 1.203 label `0` dan 584 label `1`.

| Data saat pelatihan | Accuracy | Precision (1) | Recall (1) | F1 (1) | Macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Asli saja | 98,77% | 99,65% | 96,58% | 98,09% | 98,59% |
| Asli + sintetis | 98,71% | 99,47% | 96,58% | 98,00% | 98,53% |

Kedua skenario memilih TF-IDF karakter 3–5 gram dan `C=10` melalui validation. Skenario **asli saja** dipilih sebelum evaluasi test. Penambahan data sintetis menghasilkan satu false positive tambahan pada run ini; selisih tersebut bersifat deskriptif dan belum diuji signifikansinya.

Angka lengkap ada di `test_metrics.csv` dalam folder run yang ditunjuk oleh [outputs/latest_run.json](outputs/latest_run.json). CSV memakai skala **0–1**, sedangkan tabel di atas memakai persen.

## Instalasi

Prasyarat: **Python 3.11** dan **Git**. Contoh berikut menggunakan PowerShell di Windows.

```powershell
git clone https://github.com/aidanismail/svm-classifier.git
cd svm-classifier
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Penggunaan

### Impor dataset dan jalankan eksperimen

Clone JudiScope ke folder di sebelah proyek ini jika belum tersedia:

```powershell
git clone https://github.com/atharikputra/JudiScope.git ../JudiScope
```

Impor snapshot dataset dan jalankan notebook:

```powershell
python scripts/import_athar_data.py --source ../JudiScope
python scripts/run_notebook.py
```

Notebook juga dapat dijalankan melalui VS Code atau Jupyter dengan memilih kernel `.venv` dan menjalankan **Run All**. Setiap eksekusi menyimpan hasil dalam folder run baru di `outputs/runs/`.

### Verifikasi dan ekspor hasil

```powershell
python scripts/verify_run.py
python scripts/package_run.py
```

`verify_run.py` memeriksa identitas data test, menghitung ulang metrik dari prediksi, dan memverifikasi model tersimpan. `package_run.py` membuat ZIP di `deliverables/` yang berisi kode, input, model, prediksi, tabel, grafik, dan metadata eksperimen.

Repository menyertakan tabel metrik, hasil validation, dan confusion matrix. Dataset, model, prediksi terperinci, cache, dan ZIP diabaikan Git; artefak tersebut diperoleh dengan menjalankan eksperimen atau mengekstrak bundle hasil.

### Prediksi komentar baru

Setelah model tersedia secara lokal:

```powershell
$svmRun = (Get-Content outputs/latest_run.json -Raw | ConvertFrom-Json).path
python predict.py --model "$svmRun/models/svm_original_only.joblib" --text "Videonya membantu, terima kasih"
```

Keluaran mencakup teks hasil preprocessing, prediksi kelas, dan margin keputusan SVM. Margin tersebut bukan probabilitas.

## Struktur proyek

| File/folder | Keterangan |
| --- | --- |
| `svm_experiments.ipynb` | Notebook eksperimen, evaluasi, dan analisis kesalahan |
| `docs/` | Panduan metode dan catatan lingkungan eksekusi |
| `config/` | Parameter eksperimen dan identitas dataset |
| `scripts/` | Impor dataset, eksekusi notebook, verifikasi, dan packaging |
| `data_contract.py` | Validasi input dan kesesuaian pembagian data |
| `preprocessing.py` | Cleaning teks sesuai pipeline JudiScope |
| `experiment_io.py` | Menyimpan hasil dan identitas run |
| `predict.py` | Prediksi komentar menggunakan model tersimpan |
| `outputs/` | Hasil eksperimen; satu folder untuk setiap eksekusi |

## Reproduksibilitas dan keterbatasan

Hasil yang disertakan menggunakan Python 3.11.9 dan scikit-learn 1.4.2. Seluruh 16 sel kode telah dieksekusi berurutan melalui IPython dan lulus pemeriksaan numerik serta model. Eksekusi melalui kernel Jupyter dan tampilan halaman notebook penuh belum diverifikasi pada lingkungan eksekusi tersebut; empat grafik telah diperiksa terpisah. Rincian versi dan status eksekusi tersedia di [docs/LINGKUNGAN.md](docs/LINGKUNGAN.md).

Pemetaan label kerja adalah `0=nonjudi` dan `1=promosi judi`. Definisi resmi label dan proses anotasi sumber belum terkonfirmasi. Hasil dibatasi pada split yang digunakan; kemampuan pada video, periode, atau kampanye baru belum diuji.

## Dokumentasi

- [Metode dan format hasil](docs/METODE_SVM.md)
- [Lingkungan dan status eksekusi](docs/LINGKUNGAN.md)
- [Notebook eksperimen](svm_experiments.ipynb)
