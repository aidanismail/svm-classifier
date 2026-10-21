# Run from a normal PowerShell terminal with network access.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$svmRepository = 'aidanismail/svm-classifier'
$svmRemoteUrl = 'https://github.com/aidanismail/svm-classifier.git'

$svmLogin = & gh api user --jq .login
if ($LASTEXITCODE -ne 0) {
    throw 'GitHub tidak dapat diakses. Periksa jaringan; setelah jaringan tersedia gunakan gh auth login bila autentikasi diperlukan.'
}
if ($svmLogin.Trim() -ne 'aidanismail') {
    throw 'Akun GitHub aktif bukan aidanismail. Aktifkan akun yang benar terlebih dahulu.'
}
$svmDirty = & git status --porcelain
if ($svmDirty) { throw 'Commit perubahan proyek terlebih dahulu sebelum publikasi.' }
$svmHead = & git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw 'Commit lokal belum tersedia.' }

$svmPreviousAction = $ErrorActionPreference
$ErrorActionPreference = 'Continue'
$svmVisibility = & gh repo view $svmRepository --json visibility --jq .visibility 2>$null
$svmViewExit = $LASTEXITCODE
$ErrorActionPreference = $svmPreviousAction
if ($svmViewExit -eq 0) {
    if ($svmVisibility.Trim() -ne 'PUBLIC') { throw 'Repository tujuan sudah ada dengan visibility berbeda dari public yang disetujui.' }
    $svmRemoteHead = & git ls-remote $svmRemoteUrl HEAD
    if ($LASTEXITCODE -ne 0) { throw 'Tidak dapat memeriksa repository tujuan.' }
    if ($svmRemoteHead -and -not $svmRemoteHead.StartsWith($svmHead.Trim())) {
        throw 'Repository tujuan sudah berisi riwayat berbeda. Tidak dilakukan overwrite atau force-push.'
    }
} else {
    & gh repo create $svmRepository --public --description 'Klasifikasi komentar promosi judi online di YouTube menggunakan TF-IDF dan Support Vector Machine (SVM).'
    if ($LASTEXITCODE -ne 0) { throw 'Pembuatan repository GitHub gagal.' }
}
$svmRemotes = & git remote
if ($svmRemotes -contains 'origin') {
    $svmExistingRemote = & git remote get-url origin
    if ($svmExistingRemote.Trim() -ne $svmRemoteUrl) { throw 'Remote origin berbeda dari tujuan yang disetujui.' }
} else {
    & git remote add origin $svmRemoteUrl
    if ($LASTEXITCODE -ne 0) { throw 'Tidak dapat menambahkan origin.' }
}
& git push -u origin main
if ($LASTEXITCODE -ne 0) { throw 'Push gagal; commit lokal tetap tersimpan.' }
& gh repo view $svmRepository --json url,visibility --jq '{url: .url, visibility: .visibility}'
