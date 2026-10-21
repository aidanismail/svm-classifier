# svm-classifier

Klasifikasi komentar promosi judi online di YouTube menggunakan **TF-IDF + SVM** untuk tugas UTS Machine Learning.

Dataset dan pembagian train/validation/test mengikuti pipeline [JudiScope milik Athar](https://github.com/atharikputra/JudiScope). Repo ini hanya mengerjakan SVM. Hasilnya bisa diserahkan ke teman yang menyusun perbandingan dan paper.

## Mulai dari sini

Buka **[svm_experiments.ipynb](svm_experiments.ipynb)** untuk membaca langkah, kode, tabel, dan grafik yang sudah dijalankan. Penjelasan singkat istilah dan aturan eksperimen ada di [panduan metode](docs/METODE_SVM.md).

```text
Komentar bersih → TF-IDF → SVM → prediksi → evaluasi
```

TF-IDF mengubah teks menjadi angka. SVM mempelajari cara membedakan dua kelas dari angka tersebut. Implementasinya memakai `LinearSVC` dari scikit-learn.

## Hasil

Kedua skenario diuji pada **1.787 komentar asli yang sama**: 1.203 label `0` dan 584 label `1`.

| Data saat pelatihan | Accuracy | Precision (1) | Recall (1) | F1 (1) | Macro-F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Asli saja | 98,77% | 99,65% | 96,58% | 98,09% | 98,59% |
| Asli + sintetis | 98,71% | 99,47% | 96,58% | 98,00% | 98,53% |

Keduanya memilih TF-IDF karakter 3–5 gram dan `C=10` melalui validation. Skenario **asli saja** dipilih sebelum test. Pada run ini, penambahan data sintetis menghasilkan satu false positive tambahan; selisih kecil ini belum membuktikan perbedaan yang signifikan.

Angka lengkap ada di `test_metrics.csv` dalam folder run yang ditunjuk oleh [outputs/latest_run.json](outputs/latest_run.json). CSV memakai skala **0–1**, sedangkan tabel di atas memakai persen.

## Jalankan sendiri

Gunakan **Python 3.11**. Dari folder repo:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Jika belum punya clone JudiScope di sebelah folder ini:

```powershell
git clone https://github.com/atharikputra/JudiScope.git ../JudiScope
```

Ambil dataset yang sama, lalu jalankan notebook:

```powershell
python scripts/import_athar_data.py --source ../JudiScope
python scripts/run_notebook.py
```

Atau buka notebook di VS Code/Jupyter, pilih kernel `.venv`, lalu **Run All**. Importer memeriksa versi dan hash file Athar; notebook tidak membuat split baru.

## Untuk teman yang menulis paper

```powershell
python scripts/verify_run.py
python scripts/package_run.py
```

Perintah pertama memeriksa hasil run terakhir. Perintah kedua membuat **satu ZIP di `deliverables/`** berisi input, model, prediksi tiap komentar, tabel, grafik, dan catatan teknis. Serahkan ZIP itu ke penulis paper.

Di GitHub, hasil yang ditampilkan cukup dua CSV dan confusion matrix. Model, data, serta catatan teknis tetap tersedia secara lokal dan dalam ZIP; file-file tersebut tidak perlu memenuhi daftar file repo.

## Isi repo

| File/folder | Gunanya |
| --- | --- |
| `svm_experiments.ipynb` | Alur utama: data, training, evaluasi, dan pembahasan |
| `docs/` | Panduan metode dan catatan lingkungan eksekusi |
| `config/` | Parameter eksperimen serta identitas data Athar |
| `scripts/` | Impor data, jalankan notebook, periksa hasil, buat ZIP |
| `data_contract.py` | Memastikan input dan pembagian data sama dengan Athar |
| `preprocessing.py` | Cleaning yang mengikuti pipeline Athar |
| `experiment_io.py` | Menyimpan hasil dan identitas run |
| `predict.py` | Mencoba model tersimpan dengan komentar baru |
| `outputs/` | Hasil eksperimen; satu folder untuk setiap eksekusi |

`.venv` adalah lingkungan Python lokal. File di `data/athar/`, model, cache, dan ZIP sengaja diabaikan Git.

## Catatan hasil

Notebook yang disertakan telah menjalankan seluruh 16 sel kode melalui IPython dan lulus pemeriksaan numerik serta model. Eksekusi melalui kernel Jupyter dan tampilan satu halaman notebook penuh belum diverifikasi pada lingkungan ini. Empat grafik sudah diperiksa terpisah. Rincian versi ada di [catatan lingkungan](docs/LINGKUNGAN.md).

Label kerja adalah `0=nonjudi`, `1=promosi judi`; definisi label dan proses anotasi sumber belum terkonfirmasi. Hasil berlaku untuk split ini. Kemampuan pada video atau kampanye baru belum diuji.
