# Lingkungan eksekusi

Hasil yang disertakan memakai **Python 3.11.9** dengan NumPy 1.26.4, pandas 3.0.3, SciPy 1.17.1, scikit-learn 1.4.2, Matplotlib 3.10.9, joblib 1.5.3, dan IPython 9.1.0. Versi scientific ini dicantumkan dalam `requirements.txt`.

Athar mencatat Python 3.14.3 dan scikit-learn 1.8.0. Run SVM memakai versi berbeda karena paket dipasang dari cache yang tersedia pada sesi offline. Input dan pembagian data tetap sama; versi library masing-masing metode perlu disebutkan di paper.

## Yang sudah diperiksa

- Semua 16 sel kode dijalankan berurutan dalam satu sesi IPython.
- Semua 12 kandidat konvergen. Dua model akhir disimpan dan dimuat ulang.
- Prediksi, margin, identitas test, dan metrik dari confusion counts cocok.
- Struktur notebook serta empat PNG di dalamnya valid. Empat grafik diperiksa secara visual.

## Yang masih perlu diperiksa lokal

Run tersimpan memakai mode **`sequential_ipython`**. Kernel Jupyter belum diuji karena dependensinya tidak tersedia dalam sesi offline. Preview HTML dibuat, tetapi tampilan satu halaman notebook penuh belum dapat diperiksa karena pembatasan browser sandbox.

Untuk menjalankan lewat kernel Jupyter, aktifkan `.venv`, lalu:

```powershell
python -m pip install -r requirements.txt
python scripts/run_notebook.py
```

Jika hanya paket scientific dan IPython tersedia, `python scripts/run_notebook.py --sequential` menjalankan seluruh sel dengan mode fallback tersebut. Mode ini dicatat pada output dan tidak dianggap sebagai pengujian kernel Jupyter.

Setiap eksekusi membuat folder run baru. Gunakan model, prediksi, dan tabel dari run yang sama. Muat model joblib dengan versi scikit-learn yang sesuai.
