"""Muat dan verifikasi snapshot bersama; identitas record selalu source_row."""
import json
from pathlib import Path
import pandas as pd
from experiment_io import require, sha256_file
from preprocessing import clean_comment


def verify_input_hashes(root):
    root = Path(root)
    contract = json.loads((root/'config/upstream_manifest.json').read_text(encoding='utf-8'))
    hashes = {}
    for name, record in contract['files'].items():
        path = root/'data/athar'/name
        require(path.is_file(), f'Input belum ada: {name}. Jalankan scripts/import_athar_data.py.')
        hashes[name] = sha256_file(path)
        require(hashes[name] == record['sha256'], f'Hash input berbeda: {name}. Impor ulang commit yang ditetapkan.')
    return contract, hashes


def load_shared_data(root):
    root = Path(root)
    contract, hashes = verify_input_hashes(root)

    def read(name):
        return pd.read_csv(root/'data/athar'/name, dtype=str, keep_default_na=False, encoding='utf-8-sig')

    original = read('komentar_cleaned.csv')
    synthetic = read('komentar_synthetic_only.csv')
    combined = read('komentar_10000_with_synthetic.csv')
    manifest = read('original_split_manifest.csv')
    required = {'source_row', 'komentar', 'komentar_processed', 'label'}
    for name, frame in [('original', original), ('synthetic', synthetic), ('combined', combined)]:
        require(required <= set(frame.columns), f'Kolom wajib tidak lengkap: {name}')
        require(frame['label'].isin(['0', '1']).all(), f'Label tidak valid: {name}')
        require(frame['komentar_processed'].str.strip().ne('').all(), f'Teks kosong: {name}')
        require(frame['komentar_processed'].is_unique, f'Teks duplikat: {name}')
        require(frame['komentar'].map(clean_comment).equals(frame['komentar_processed']), f'Cleaning tidak identik: {name}')
    require(len(original) == contract['counts']['original'], 'Jumlah original berbeda.')
    require(len(synthetic) == contract['counts']['synthetic'], 'Jumlah synthetic berbeda.')
    require(len(combined) == contract['counts']['combined'], 'Jumlah combined berbeda.')
    require(original['source_row'].is_unique and original['source_row'].ne('').all(), 'ID original tidak unik/kosong.')
    require(set(manifest.columns) == {'source_row', 'split'}, 'Schema manifest berbeda.')
    require(manifest['source_row'].is_unique, 'ID manifest duplikat.')
    require(set(manifest['source_row']) == set(original['source_row']), 'Cakupan manifest berbeda.')
    require(set(manifest['split']) == set(contract['split_counts']), 'Bagian manifest tidak valid.')
    require({'is_synthetic', 'data_origin', 'synthetic_id', 'generator_version'} <= set(combined), 'Provenance combined tidak lengkap.')
    require(combined['is_synthetic'].isin(['True', 'False']).all(), 'Flag synthetic tidak valid.')
    require(synthetic['label'].eq('1').all() and synthetic['is_synthetic'].eq('True').all(), 'Synthetic bukan positif/flag salah.')
    require(synthetic['data_origin'].eq('synthetic_template').all(), 'Asal synthetic berbeda.')
    require(synthetic['generator_version'].eq('template_v1').all(), 'Versi generator berbeda.')
    require(synthetic['synthetic_id'].is_unique, 'ID synthetic duplikat.')
    for column in ['source_row', 'video_id', 'title', 'channel_name', 'tanggal', 'author']:
        require(synthetic[column].eq('').all(), f'Metadata synthetic tidak kosong: {column}')
    combined_original = combined.loc[combined['is_synthetic'].eq('False')]
    require(combined_original['data_origin'].eq('source_dataset').all(), 'Asal original berbeda.')
    pd.testing.assert_frame_equal(original.reset_index(drop=True), combined_original[original.columns].reset_index(drop=True))
    pd.testing.assert_frame_equal(synthetic.reset_index(drop=True), combined.loc[combined['is_synthetic'].eq('True')].reset_index(drop=True))
    require(set(original['komentar_processed']).isdisjoint(synthetic['komentar_processed']), 'Original/synthetic bertumpang tindih.')
    data = manifest.merge(original, on='source_row', how='left', validate='one_to_one', sort=False)
    require(data['source_row'].tolist() == manifest['source_row'].tolist(), 'Urutan manifest berubah.')
    parts = {name: data.loc[data['split'].eq(name)].copy().reset_index(drop=True) for name in contract['split_counts']}
    for name, frame in parts.items():
        require(len(frame) == contract['split_counts'][name], f'Jumlah split berbeda: {name}')
        require(frame['label'].value_counts().to_dict() == contract['class_counts'][name], f'Distribusi kelas berbeda: {name}')
        frame['label'] = frame['label'].astype(int)
    synthetic['label'] = synthetic['label'].astype(int)
    return {'original': original, 'synthetic': synthetic, 'parts': parts, 'contract': contract, 'hashes': hashes}
