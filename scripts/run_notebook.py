"""Jalankan notebook dari awal; mode sequential dinyatakan eksplisit bila kernel tidak tersedia."""
import argparse
import importlib.util
import json
import os
import platform
from pathlib import Path
import sys
import traceback


def run_sequential(path):
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    shell = InteractiveShell.instance()
    notebook = json.loads(path.read_text(encoding='utf-8'))
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            cell['execution_count'], cell['outputs'] = None, []
    notebook['metadata']['execution_mode'] = 'sequential_ipython'
    notebook['metadata']['language_info']['version'] = platform.python_version()
    notebook['metadata']['execution_note'] = 'Sel kode dieksekusi berurutan dalam satu namespace IPython. Transport/kernel Jupyter belum diverifikasi pada run ini.'
    counter = 0
    for index, cell in enumerate(notebook['cells']):
        if cell['cell_type'] != 'code':
            continue
        counter += 1
        print(f'Executing cell {counter} (index {index})', flush=True)
        with capture_output(stdout=True, stderr=True, display=True) as captured:
            result = shell.run_cell(''.join(cell['source']), store_history=False)
        outputs = []
        for name, value in [('stdout',captured.stdout), ('stderr',captured.stderr)]:
            if value:
                outputs.append({'output_type':'stream', 'name':name, 'text':value})
        for item in captured.outputs:
            outputs.append({'output_type':'display_data', 'data':item.data, 'metadata':item.metadata})
        cell['execution_count'] = counter
        cell['outputs'] = outputs
        error = result.error_before_exec or result.error_in_exec
        if error:
            cell['outputs'].append({'output_type':'error','ename':type(error).__name__,'evalue':str(error),'traceback':traceback.format_exception(error)})
        path.write_text(json.dumps(notebook, ensure_ascii=False, indent=1)+'\n', encoding='utf-8')
        if error:
            raise RuntimeError(f'Cell {counter} gagal: {error}') from error
    return notebook


def run_kernel(path, root):
    import subprocess
    import nbformat
    from nbclient import NotebookClient
    if sys.prefix == sys.base_prefix:
        raise RuntimeError('Aktifkan .venv terlebih dahulu agar kernelspec dipasang hanya di environment proyek.')
    subprocess.run([sys.executable,'-m','ipykernel','install','--prefix',sys.prefix,'--name','svm-classifier','--display-name','Python (svm-classifier)'],check=True)
    notebook = nbformat.read(path, as_version=4)
    notebook.metadata['execution_mode'] = 'jupyter_kernel'
    notebook.metadata['execution_note'] = 'Notebook dieksekusi dari awal melalui kernel Jupyter svm-classifier pada environment proyek.'
    NotebookClient(notebook, timeout=600, kernel_name='svm-classifier', resources={'metadata':{'path':str(root)}}).execute()
    nbformat.validate(notebook)
    nbformat.write(notebook, path)
    return notebook


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sequential', action='store_true', help='Fallback eksplisit: jalankan kode melalui IPython, bukan kernel Jupyter.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    os.chdir(root)
    sys.path.insert(0,str(root))
    (root/'.cache/ipython').mkdir(parents=True,exist_ok=True)
    (root/'.cache/matplotlib').mkdir(parents=True,exist_ok=True)
    os.environ['IPYTHONDIR'] = str(root/'.cache/ipython')
    os.environ['MPLCONFIGDIR'] = str(root/'.cache/matplotlib')
    os.environ['MPLBACKEND'] = 'Agg'
    os.environ['SVM_EXECUTION_MODE'] = 'sequential_ipython' if args.sequential else 'jupyter_kernel'
    path = root/'svm_experiments.ipynb'
    if not args.sequential:
        missing = [p for p in ['nbformat','nbclient','ipykernel','zmq'] if importlib.util.find_spec(p) is None]
        if missing:
            raise SystemExit(f'Komponen Jupyter belum tersedia: {missing}. Pasang requirements.txt, atau gunakan --sequential untuk menjalankan sel melalui IPython.')
    notebook = run_sequential(path) if args.sequential else run_kernel(path, root)
    print('Notebook selesai:',path.name)
    print('Mode:',notebook['metadata']['execution_mode'])
