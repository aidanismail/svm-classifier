# Lingkungan dan status eksekusi

## Run yang disertakan

Scientific dependencies dipasang dari cache wheel lokal karena sesi pengerjaan memblokir akses jaringan. Kode eksperimen tetap menggunakan snapshot input, grid fitur/C, pemisahan, dan aturan seleksi yang disetujui.

| Komponen | Upstream tercatat | Run SVM ini |
| --- | --- | --- |
| Python | 3.14.3 | 3.11.9 |
| NumPy | 2.4.4 | 1.26.4 |
| pandas | 3.0.2 | 3.0.3 |
| SciPy | tidak tercatat di ringkasan upstream | 1.17.1 |
| scikit-learn | 1.8.0 | 1.4.2 |
| Matplotlib | 3.10.8 | 3.10.9 |
| joblib | 1.5.3 | 1.5.3 |
| IPython | tidak tercatat | 9.1.0 |

Perbedaan versi bersifat eksplisit. Kesamaan input dan protokol tidak menjamin implementasi solver/numerik dua versi library identik. Cantumkan lingkungan masing-masing metode pada paper dan jangan menafsirkan waktu dari komputer berbeda sebagai ranking kecepatan yang terkontrol.

## Yang sudah dijalankan

- Seluruh 16 sel kode notebook dieksekusi dalam satu namespace IPython, dari awal sampai akhir.
- Seluruh 12 kandidat konvergen, dua model di-refit, dan dua skenario diuji.
- Metrik dihitung ulang dari prediksi ekspor memakai rumus confusion counts.
- Kedua pipeline dimuat ulang dan prediksi serta marginnya cocok; koefisien fitur diverifikasi.
- Format notebook diperiksa terhadap schema v4.5 dari wheel resmi nbformat 5.10.4; 16 execution count berurutan, tanpa error output, dan empat PNG embedded valid.
- Keempat PNG diperiksa secara visual; sel, tabel, dan narasi juga ditinjau dari sumber/output yang disimpan.

## Yang belum diverifikasi

Eksekusi melalui transport/kernel Jupyter belum diverifikasi. Paket `nbformat`, `nbclient`, `ipykernel`, dan binary `pyzmq` yang cocok tidak tersedia pada environment offline awal. Mode run adalah `sequential_ipython`, bukan `jupyter_kernel`.

Preview HTML notebook berhasil dibuat, tetapi inspeksi visual keseluruhan halaman melalui browser headless terhalang pembatasan proses/IPC Windows sandbox. Pemeriksaan PNG terpisah dan validasi struktur/output tidak diklaim menggantikan pemeriksaan visual halaman notebook penuh.

Setelah jaringan/dependensi tersedia, jalankan:

```powershell
python -m pip install -r requirements-notebook.txt
python scripts/run_notebook.py
```

Ini membuat run baru, mempertahankan grid yang sama, memeriksa format melalui nbformat, dan mengeksekusi dengan kernel `.venv`. Jika mode/kernel berubah, laporkan run ID baru beserta hasilnya; jangan mencampur prediksi dan model dari run lama.

Scientific requirements pada `requirements.txt` mencerminkan versi yang benar-benar dipakai, dan `requirements-executed.txt` mencatat paket environment saat pengiriman. Memuat model joblib dengan versi scikit-learn berbeda tidak menjadi jalur reproduksi yang disarankan.
