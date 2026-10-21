"""Verifikasi numerik independen dari prediksi ekspor, tanpa training ulang."""
import argparse
from collections import Counter
import csv
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from data_contract import verify_input_hashes
from experiment_io import require, sha256_file, text_sha256, utc_now, write_json, code_fingerprints


def read_csv(path):
    with Path(path).open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))


def scores_from_counts(tn, fp, fn, tp):
    """Rumus dari hitungan; tidak memakai sklearn.metrics/notebook helper."""
    divide = lambda a, b: a / b if b else 0.0
    f1_positive = divide(2 * tp, 2 * tp + fp + fn)
    f1_negative = divide(2 * tn, 2 * tn + fp + fn)
    return {'accuracy': divide(tn + tp, tn + fp + fn + tp),
            'precision_1': divide(tp, tp + fp), 'recall_1': divide(tp, tp + fn),
            'f1_1': f1_positive, 'macro_f1': (f1_positive + f1_negative) / 2}


def verify_run(root, run_dir, check_models=True, save=True):
    root, run_dir = Path(root).resolve(), Path(run_dir).resolve()
    contract, hashes = verify_input_hashes(root)
    summary = json.loads((run_dir/'experiment_summary.json').read_text(encoding='utf-8'))
    lock = json.loads((run_dir/'selection_locked.json').read_text(encoding='utf-8'))
    require(summary['run_id'] == run_dir.name == lock['run_id'], 'Run ID tidak konsisten.')
    require(summary['config_sha256'] == sha256_file(root/'config/experiment_config.json') == lock['config_sha256'], 'Konfigurasi berubah.')
    require(summary['input_hashes'] == hashes == lock['input_hashes'], 'Hash input antarartefak berbeda.')
    require(summary['code_fingerprints'] == code_fingerprints(root), 'Kode eksperimen berubah sejak run; gunakan kode yang direkam atau buat run baru.')
    require(summary['selection_sha256'] == sha256_file(run_dir/'selection_locked.json'), 'Selection record berubah.')
    require(lock['validation_results_sha256'] == sha256_file(run_dir/'validation_results.csv'), 'Hasil validation berubah.')
    require(lock['locked_at'] <= summary['test_evaluation_started_at'], 'Selection dibuat sesudah evaluasi test.')
    originals = {r['source_row']: r for r in read_csv(root/'data/athar/komentar_cleaned.csv')}
    manifest = read_csv(root/'data/athar/original_split_manifest.csv')
    test_ids = [r['source_row'] for r in manifest if r['split'] == 'test']
    predictions = read_csv(run_dir/'test_predictions.csv')
    metrics = read_csv(run_dir/'test_metrics.csv')
    errors = read_csv(run_dir/'test_errors.csv')
    tuning = read_csv(run_dir/'validation_results.csv')
    config = json.loads((root/'config/experiment_config.json').read_text(encoding='utf-8'))
    reports = json.loads((run_dir/'classification_reports.json').read_text(encoding='utf-8'))
    require(len(predictions) == 3574 and len(metrics) == 2, 'Jumlah prediksi/metrik berbeda dari kontrak.')
    require(len(tuning) == 12 and all(r['converged'] == 'True' for r in tuning), 'Tuning tidak lengkap atau belum konvergen.')
    expected_candidates = {(arm, feature, float(c)) for arm in config['scenarios'] for feature in config['features'] for c in config['C_values']}
    require({(r['scenario'],r['features'],float(r['C'])) for r in tuning} == expected_candidates, 'Grid tuning berbeda.')
    feature_order = config['selection']['feature_ties']
    winners = {}
    for arm in config['scenarios']:
        candidates = [r for r in tuning if r['scenario'] == arm]
        winner = min(candidates, key=lambda r: (-float(r['f1_1']), -float(r['macro_f1']), feature_order.index(r['features']), float(r['C'])))
        winners[arm] = winner
        require(lock['best_per_scenario'][arm]['features'] == winner['features'] and float(lock['best_per_scenario'][arm]['C']) == float(winner['C']), f'Seleksi tidak mengikuti validation: {arm}')
    preferred = min(config['scenarios'], key=lambda arm: (-float(winners[arm]['f1_1']),-float(winners[arm]['macro_f1']),config['scenarios'].index(arm)))
    require(lock['preferred_scenario'] == summary['preferred_scenario'] == preferred, 'Skenario pilihan tidak mengikuti validation.')
    require(len({(r['scenario'],r['source_row']) for r in predictions}) == len(predictions), 'Kunci prediksi duplikat.')
    require(len({(r['scenario'],r['source_row']) for r in errors}) == len(errors), 'Kunci error duplikat.')
    checks = ['canonical_input_hashes', 'run_config_identity', 'source_code_fingerprints', 'validation_grid_and_selection', 'pretest_selection_receipt', 'prediction_keys']
    recomputed = {}
    for arm in config['scenarios']:
        rows = [r for r in predictions if r['scenario'] == arm]
        require([r['source_row'] for r in rows] == test_ids, f'Urutan/ID test berbeda: {arm}')
        for row in rows:
            canonical = originals[row['source_row']]
            require(row['run_id'] == run_dir.name and row['method'] == 'SVM' and row['split'] == 'test', 'Identitas prediksi salah.')
            require(row['label'] == canonical['label'] and row['processed_text_sha256'] == text_sha256(canonical['komentar_processed']), 'Label/hash teks prediksi salah.')
            require(row['prediction'] in {'0','1'} and math.isfinite(float(row['decision_score'])), 'Prediksi/margin tidak valid.')
        counts = Counter((int(r['label']), int(r['prediction'])) for r in rows)
        tn, fp, fn, tp = (counts[(0,0)], counts[(0,1)], counts[(1,0)], counts[(1,1)])
        result = scores_from_counts(tn, fp, fn, tp)
        metric_rows = [r for r in metrics if r['scenario'] == arm]
        require(len(metric_rows) == 1, 'Baris metrik skenario salah.')
        reported = metric_rows[0]
        require(reported['run_id'] == run_dir.name and reported['method'] == 'SVM' and reported['classifier'] == 'LinearSVC', 'Identitas metrik salah.')
        require(int(reported['fit_rows']) == (7147 if arm == 'original_only' else 8213) and int(reported['test_rows']) == 1787, 'Jumlah fitting/test salah.')
        require(reported['features'] == winners[arm]['features'] and float(reported['C']) == float(winners[arm]['C']), 'Parameter metrik salah.')
        for field, expected in result.items():
            require(math.isclose(float(reported[field]), expected, abs_tol=1e-12), f'Metrik {field} salah: {arm}')
            require(math.isclose(float(summary['test_metrics'][arm][field]), expected, abs_tol=1e-12), f'Ringkasan metrik {field} salah.')
        require([int(reported[k]) for k in ['tn','fp','fn','tp']] == [tn,fp,fn,tp], 'Confusion counts tidak cocok.')
        require(summary['confusion_matrices'][arm] == [[tn,fp],[fn,tp]], 'Confusion matrix summary salah.')
        require(int(reports[arm]['0']['support']) == 1203 and int(reports[arm]['1']['support']) == 584, 'Support report salah.')
        mismatch_ids = {r['source_row'] for r in rows if r['label'] != r['prediction']}
        error_rows = [r for r in errors if r['scenario'] == arm]
        require({r['source_row'] for r in error_rows} == mismatch_ids, 'ID error tidak cocok.')
        prediction_by_id = {r['source_row']: r for r in rows}
        for error in error_rows:
            record = originals[error['source_row']]
            require(all(error[k] == prediction_by_id[error['source_row']][k] for k in prediction_by_id[error['source_row']]), 'Isi error berbeda dari prediksi.')
            require(error['komentar'] == record['komentar'] and error['komentar_processed'] == record['komentar_processed'], 'Teks error salah.')
            require(error['error_type'] == ('false_positive' if error['label'] == '0' else 'false_negative'), 'Jenis error salah.')
        if check_models:
            import joblib
            import numpy as np
            model = joblib.load(run_dir/'models'/f'svm_{arm}.joblib')
            require(list(model.classes_) == [0,1], 'Urutan kelas model salah.')
            text = [originals[key]['komentar_processed'] for key in test_ids]
            require(np.array_equal(model.predict(text), [int(r['prediction']) for r in rows]), 'Prediksi model setelah reload berbeda.')
            require(np.allclose(model.decision_function(text), [float(r['decision_score']) for r in rows], rtol=0, atol=1e-10), 'Margin reload berbeda.')
            require(float(model.named_steps['svm'].C) == float(winners[arm]['C']), 'Parameter model tidak cocok.')
            for field, expected in {**config['svm'],'random_state':config['seed']}.items():
                require(model.named_steps['svm'].get_params()[field] == expected, f'Parameter SVM berbeda: {field}')
            vector_options = {**config['tfidf'],**config['features'][winners[arm]['features']]}
            vector_options['ngram_range'] = tuple(vector_options['ngram_range'])
            for field, expected in vector_options.items():
                require(model.named_steps['tfidf'].get_params()[field] == expected, f'Parameter TF-IDF berbeda: {field}')
            if arm == preferred:
                weights = read_csv(run_dir/'selected_model_feature_weights.csv')
                terms = model.named_steps['tfidf'].get_feature_names_out()
                require([r['feature'] for r in weights] == terms.tolist(), 'Nama fitur ekspor berbeda.')
                require(np.allclose([float(r['coefficient']) for r in weights], model.named_steps['svm'].coef_[0], rtol=0, atol=1e-12), 'Koefisien fitur berbeda.')
        recomputed[arm] = {'tn': tn, 'fp': fp, 'fn': fn, 'tp': tp, **result}
    checks += ['exact_test_identity_labels_and_text', 'independent_metric_formulas', 'confusion_matrices', 'error_records', 'class_supports']
    if check_models:
        checks += ['both_serialized_model_predictions', 'both_serialized_model_margins_atol_1e-10', 'selected_feature_alignment']
    receipt = {'schema_version': '1.0', 'run_id': run_dir.name, 'status': 'passed', 'checked_at': utc_now(), 'checks': checks,
               'recomputed': recomputed, 'notebook_execution_mode': summary['execution_mode'],
               'jupyter_kernel_verified': summary['execution_mode'] == 'jupyter_kernel',
               'limitations': ['Verifikasi konsistensi artefak tidak membuktikan kebenaran anotasi atau generalisasi ke video baru.']}
    if save:
        write_json(run_dir/'verification.json', receipt)
    return receipt


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--root', default=ROOT, type=Path)
    parser.add_argument('--skip-models', action='store_true', help='Verifikasi tabel saja; tidak menyatakan model terverifikasi.')
    args = parser.parse_args()
    result = verify_run(args.root, args.run, check_models=not args.skip_models, save=False)
    print(json.dumps(result, ensure_ascii=False, indent=2))
