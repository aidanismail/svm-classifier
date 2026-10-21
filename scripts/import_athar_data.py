"""Impor enam file dari commit Athar yang dipatok; tidak mengimpor hasil model."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def import_snapshot(source, root):
    contract = json.loads((root/'config/upstream_manifest.json').read_text(encoding='utf-8'))
    staged = {}
    for name, record in contract['files'].items():
        # stdout berupa bytes, sehingga BOM dan line endings tetap identik.
        result = subprocess.run(['git', '-C', str(source), 'show', f"{contract['commit']}:{record['path']}"], capture_output=True, check=True)
        digest = hashlib.sha256(result.stdout).hexdigest()
        if digest != record['sha256']:
            raise ValueError(f'Hash upstream tidak cocok: {name}')
        staged[name] = result.stdout
    destination = root/'data/athar'
    destination.mkdir(parents=True, exist_ok=True)
    for name, content in staged.items():
        target = destination/name
        temporary = target.with_name(target.name + '.tmp')
        temporary.write_bytes(content)
        temporary.replace(target)
    print(f"Impor {len(staged)} file terverifikasi dari commit {contract['commit']}.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Clone lokal JudiScope, dapat berada di commit lain.')
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    import_snapshot(args.source.resolve(), args.root.resolve())
