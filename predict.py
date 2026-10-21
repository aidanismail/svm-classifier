"""Prediksi komentar mentah memakai pipeline TF-IDF + SVM yang tersimpan."""
import argparse
import json
from pathlib import Path
import joblib
from preprocessing import clean_comment


def predict_comments(model_path, comments):
    model = joblib.load(model_path)
    processed = [clean_comment(text) for text in comments]
    if any(not text for text in processed):
        raise ValueError('Komentar kosong setelah cleaning.')
    if list(model.classes_) != [0, 1]:
        raise ValueError('Urutan kelas model harus [0, 1].')
    labels = model.predict(processed)
    margins = model.decision_function(processed)
    return [{'komentar': raw, 'komentar_processed': clean, 'prediction': int(label), 'decision_score': float(margin)}
            for raw, clean, label, margin in zip(comments, processed, labels, margins)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--text', required=True, action='append', help='Boleh diulang untuk beberapa komentar.')
    args = parser.parse_args()
    print(json.dumps(predict_comments(args.model, args.text), ensure_ascii=False, indent=2))
