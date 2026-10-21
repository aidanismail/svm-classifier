"""Penulisan atomik dan identitas artefak; tidak berisi training model."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text_sha256(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    temporary.replace(path)


def write_csv(frame, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    frame.to_csv(temporary, index=False, encoding='utf-8-sig', lineterminator='\n')
    temporary.replace(path)


def code_fingerprints(root):
    root = Path(root)
    files = [*root.glob('*.py'), *root.glob('scripts/*.py'), *root.glob('config/*.json')]
    result = {p.relative_to(root).as_posix(): sha256_file(p) for p in sorted(files)}
    notebook = json.loads((root/'svm_experiments.ipynb').read_text(encoding='utf-8'))
    code = [''.join(cell['source']) for cell in notebook['cells'] if cell['cell_type'] == 'code']
    result['svm_experiments.ipynb:code_cells'] = text_sha256(json.dumps(code, ensure_ascii=False))
    return result


def git_identity(root):
    revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True)
    dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=root, capture_output=True, text=True)
    return {'commit': revision.stdout.strip() if revision.returncode == 0 else None, 'dirty': bool(dirty.stdout.strip())}


def write_artifact_manifest(run_dir):
    run_dir = Path(run_dir)
    files = []
    for path in sorted(run_dir.rglob('*')):
        if path.is_file() and path.name != 'artifact_manifest.json' and not path.name.endswith('.tmp'):
            files.append({'path': path.relative_to(run_dir).as_posix(), 'bytes': path.stat().st_size, 'sha256': sha256_file(path)})
    write_json(run_dir/'artifact_manifest.json', {'schema_version': '1.0', 'run_id': run_dir.name, 'files': files})
