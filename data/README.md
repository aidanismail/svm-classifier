# Snapshot dataset bersama

Data diimpor byte demi byte dari [JudiScope](https://github.com/atharikputra/JudiScope), commit `d9c7feb47aeac1f2889e19c2cddc255525e358ef`. Importer mengambil enam keluaran preparation: cleaned, synthetic-only, combined, split manifest, dan dua summary. Tidak ada hasil classifier upstream yang diimpor.

```powershell
python scripts/import_athar_data.py --source ../JudiScope
```

Path clone boleh berbeda. Importer membaca commit yang dipatok melalui `git show`; tidak perlu memindahkan branch checkout. Semua fingerprint, jumlah, dan distribusi label berada pada `config/upstream_manifest.json`.

Notebook 01 upstream menghasilkan 8.934 original unik dari 10.230 record mentah; notebook 02 menghasilkan 1.066 synthetic dengan seed `20261019` dan `template_v1`. Untuk regenerasi, gunakan commit upstream yang sama, jalankan notebook 01 lalu 02, dan verifikasi fingerprint sebelum menggunakan hasilnya. Notebook SVM tidak menjalankan generator baru dan tidak membagi ulang CSV gabungan.

Sumber awal berdasarkan informasi tim adalah [Judi Online, Kaggle yaemico/judionline](https://www.kaggle.com/datasets/yaemico/judionline). Lisensi, versi dataset sumber, anotasi, dan definisi resmi label belum terkonfirmasi. Tidak ada lisensi baru yang diberikan terhadap dataset ini. Synthetic merupakan buatan tim, bukan komentar tambahan yang dikumpulkan dari YouTube/Kaggle.

File snapshot di `data/athar/` diabaikan Git untuk menjaga pemisahan kode dan data. Snapshot yang benar-benar digunakan disertakan pada handoff bundle lokal. ID `source_row` tidak boleh dinomori ulang. Working labels `0=nonjudi`, `1=promosi judi` tetap membawa keterbatasan sumber.
