"""Buat bundle lokal berisi kode, input, dan bukti SVM; tidak mengunggah ke layanan lain."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from experiment_io import require, sha256_file
from scripts.verify_run import verify_run


def package_run(root, run_dir):
    root, run_dir = Path(root).resolve(), Path(run_dir).resolve()
    require(run_dir.parent == root/'outputs/runs', 'Pilih run di outputs/runs milik proyek ini.')
    verify_run(root, run_dir, check_models=True, save=False)
    manifest = json.loads((run_dir/'artifact_manifest.json').read_text(encoding='utf-8'))
    for record in manifest['files']:
        path = (run_dir/record['path']).resolve()
        require(path.is_relative_to(run_dir), 'Path artefak di luar run.')
        require(path.stat().st_size == record['bytes'] and sha256_file(path) == record['sha256'], f"Artefak berubah: {record['path']}")
    files = [*root.glob('*.py'), *root.glob('*.md'), *root.glob('*.txt'), root/'.gitignore', root/'.gitattributes', root/'svm_experiments.ipynb']
    for folder in ['scripts','config','docs','data']:
        files += [p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.name.endswith('.tmp')]
    files += [p for p in run_dir.rglob('*') if p.is_file() and not p.name.endswith('.tmp')]
    files = sorted(set(files))
    names = [p.relative_to(root).as_posix() for p in files]
    require('svm_experiments.ipynb' in names and 'data/athar/original_split_manifest.csv' in names, 'Bundle tidak lengkap.')
    for name in ['svm_original_only.joblib','svm_with_synthetic.joblib','test_predictions.csv','test_metrics.csv','verification.json']:
        require(any(p.name == name for p in files), f'Bukti wajib tidak ada: {name}')
    bundle_manifest = {'schema_version':'1.0','run_id':run_dir.name,'files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha256_file(p)} for p in files]}
    destination = root/'deliverables'/f'svm_{run_dir.name}.zip'
    destination.parent.mkdir(exist_ok=True)
    temporary = destination.with_suffix('.zip.tmp')
    with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path,path.relative_to(root).as_posix())
        archive.writestr('BUNDLE_MANIFEST.json',json.dumps(bundle_manifest,ensure_ascii=False,indent=2))
    with zipfile.ZipFile(temporary) as archive:
        require(archive.testzip() is None,'CRC archive gagal.')
        for record in bundle_manifest['files']:
            content = archive.read(record['path'])
            require(len(content) == record['bytes'] and hashlib.sha256(content).hexdigest() == record['sha256'],f"Hash bundle gagal: {record['path']}")
    temporary.replace(destination)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',required=True,type=Path)
    args = parser.parse_args()
    path = package_run(ROOT,args.run)
    print('Bundle terverifikasi:',path)
    print('SHA-256:',sha256_file(path))
