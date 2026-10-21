> Disetujui pengguna pada 21 Oktober 2026. Publikasi diminta ke aidanismail/svm-classifier (public). Status pelaksanaan aktual dan keterbatasan lingkungan dijelaskan dalam README dan docs/LINGKUNGAN.md.

# svm-classifier: final implementation plan

Status: **approved and implemented**. The original plan below records the agreed scope. See README and docs/LINGKUNGAN.md for the actual execution mode, environment differences, and publication status.

## 1. Project identity and ownership

Repository name: **`svm-classifier`**.

Repository description:

> Klasifikasi komentar promosi judi online di YouTube menggunakan TF-IDF dan Support Vector Machine (SVM), dengan dataset serta pembagian eksperimen yang konsisten untuk proyek kelompok UTS.

The group has four members:

| Member | Responsibility |
| --- | --- |
| User | TF-IDF + SVM implementation, evaluation, explanation, and evidence |
| ANN teammate | ANN implementation and results |
| Athar | Naive Bayes implementation and the shared dataset-preparation pipeline |
| Fourth teammate | Compare all three methods and assemble the paper |

This repository implements and reports **SVM only**. It delivers trustworthy, inspectable SVM evidence for the fourth teammate. It does not import other classifiers' scores or predictions, run a cross-method comparison, rank the methods, implement ANN/Naive Bayes, or write the complete group paper. Original-only versus synthetic-augmented training are two scenarios of this SVM experiment.

The classifier is `LinearSVC`; TF-IDF is its input representation. IndoBERT is excluded. Execution targets local Jupyter/VS Code on CPU. The research objective is a reproducible, understandable comparison contribution, not a predetermined score or a requirement to outperform another method.

## 2. Repository and deliverable structure

Create `UTS/svm-classifier/` as an independent local Git repository beside `UTS/JudiScope/`, after approval. Athar's tracked files remain unchanged. Do not create or publish a GitHub remote until its destination and publication instructions are supplied.

```text
svm-classifier/
  README.md                          purpose, reading order, setup, actual SVM results
  EXPERIMENT_PLAN.md                 approved copy of this plan
  requirements.txt                  pinned scientific and notebook dependencies
  .gitignore
  .gitattributes
  svm_experiments.ipynb              main explained, executed experiment
  data_contract.py                  input loading, identity and split validation
  preprocessing.py                  shared deterministic raw-text cleaning
  predict.py                        inference using a saved SVM pipeline
  scripts/
    import_athar_data.py             verified import from the pinned upstream pipeline
    verify_run.py                    independently recompute and verify exported results
    package_run.py                   create a complete local handoff bundle
  config/
    upstream_manifest.json          upstream commit, paths, hashes, expected counts
    experiment_config.json          feature grid, SVM parameters, selection rules
  data/
    README.md                        attribution and exact import/reproduction steps
    athar/                          canonical imported data and preparation summaries
  docs/
    METODE_SVM.md                    readable explanation of this method
    HASIL_SVM.md                     observed SVM results and error discussion
    KONTRAK_HASIL.md                 artifact schemas and instructions for the paper owner
  outputs/
    runs/<run_id>/
      selection_locked.json
      validation_results.csv
      test_metrics.csv
      test_predictions.csv
      test_errors.csv
      selected_model_feature_weights.csv
      classification_reports.json
      experiment_summary.json
      verification.json
      artifact_manifest.json
      models/
        svm_original_only.joblib
        svm_with_synthetic.joblib
      figures/
        validation_scores.png
        confusion_matrices.png
        test_metrics.png
        selected_model_features.png
  deliverables/
    svm_<run_id>.zip                 reproducibility and review bundle
```

Keep fitting, selection, and evaluation code visible in the notebook. Helpers handle data checks, common cleaning, verification, packaging, and inference. Avoid a large framework or application that makes the academic method harder to follow.

Track code, configuration, documentation, the executed notebook, and selected aggregate results/figures. Ignore environments, caches, imported comment-level data, generated model binaries, run-local prediction data, and delivery archives by default. The handoff bundle explicitly includes the necessary local inputs, prediction-level evidence, and models so reviewers are not left with aggregate screenshots alone. Document the import and packaging commands. Preserve upstream attribution and its unresolved dataset-license details without assigning a new license to that data.

## 3. Canonical dataset: Athar's pipeline

Use the outputs of Athar's cleaning and generator notebooks at upstream commit **`d9c7feb47aeac1f2889e19c2cddc255525e358ef`** from `https://github.com/atharikputra/JudiScope`.

Import the existing output bytes, preserving text, record identities, BOM, and line endings. The importer reads the pinned commit or verifies local source files against its expected hashes. It does not trust a mutable `main` checkout, redo cleaning differently, generate different synthetic comments, or create another split.

Canonical imports into `data/athar/`:

| File | Purpose |
| --- | --- |
| `komentar_cleaned.csv` | 8,934 cleaned original comments |
| `komentar_synthetic_only.csv` | 1,066 generated positive comments |
| `komentar_10000_with_synthetic.csv` | Cross-check original/synthetic exports; never split it randomly |
| `original_split_manifest.csv` | Shared original train/validation/test membership |
| `cleaning_summary.json` | Preparation decisions and provenance |
| `augmentation_summary.json` | Generator configuration and provenance |

The manifest happens to live under upstream `outputs/bayesian/`; it is imported solely as the shared split definition. No Bayesian model, metric, or prediction file is imported.

### Fixed input fingerprints

| Upstream path | SHA-256 |
| --- | --- |
| `outputs/cleaning/komentar_cleaned.csv` | `5748b86c1d1d72c9e29023b8311e692f0fbebe3edc9fe556df6a5b4c75b3feb3` |
| `outputs/augmentation/komentar_synthetic_only.csv` | `4ac721c4a2aa5da53aae12ff0a177f5a9a384b5c387aa481839ed67cf3002c0c` |
| `outputs/augmentation/komentar_10000_with_synthetic.csv` | `3624f73dc131499dd57fbc6195d593fb829fabba90af7a923b33944114dd8303` |
| `outputs/bayesian/original_split_manifest.csv` | `1512e44e643cfbf666895fadcba550fd17111a1caef9584825adcbd83a0b0781` |

The raw source hash recorded in the preparation summaries is `6a31d1718093e45ad46b8083e94f64cc11f101dbe689b4428c0f5330bd0228e8`. Record/verify the preparation-summary hashes against the same pinned commit as well.

After import, the new repository works from its own snapshot without needing the sibling directory during training. Document upstream reproduction through notebooks 01 and 02 with their original generator seed `20261019` and version `template_v1`; do not automatically rerun or modify them.

### Required validation before fitting

- Read text CSVs with `dtype=str`, `keep_default_na=False`, and UTF-8 BOM handling.
- Validate source hashes, expected schemas, row counts, nonempty unique processed text, and valid binary labels.
- Confirm synthetic flags and provenance explicitly; a string `'False'` must not be interpreted as true.
- Confirm original and synthetic rows agree with the combined export and have disjoint processed texts.
- Match originals to the manifest by unique `source_row` with a complete one-to-one join and preserve manifest order.
- Confirm exact split coverage and disjoint original IDs/processed texts between partitions.
- Use only `komentar_processed` as X and `label` as y. Metadata, IDs, previous predictions, duplicate counts, and synthetic flags do not enter TF-IDF.

Working labels remain `0 = nonjudi`, `1 = promosi judi`, with the source-label uncertainty stated in the documentation. Do not relabel the test data after observing errors. Missing files, changed hashes, or broken identities stop execution with a specific explanation.

## 4. Shared experiment protocol

This contract makes SVM outputs usable in the later group comparison. The fourth teammate can verify its fingerprints, record identities, definitions, and scenario membership against the other members' deliverables. Actual comparability also requires the other methods to follow that shared contract; this repository does not certify their implementations.

Use the committed manifest, not a new `train_test_split`. Set SVM `random_state=42` where applicable.

| Stage | `original_only` | `with_synthetic` |
| --- | ---: | ---: |
| Candidate fitting | 5,360 original | 5,360 original + 1,066 synthetic = 6,426 |
| Validation | 1,787 original | The same 1,787 original |
| Final refit | 7,147 original | 7,147 original + 1,066 synthetic = 8,213 |
| Final test | 1,787 original | The same 1,787 original |

Original class counts in label order `0/1` are train `3610/1750`, validation `1203/584`, and test `1203/584`.

Select the best configuration for each scenario using validation F1 for class `1`, then validation macro-F1. Resolve exact remaining ties by fixed feature order (`word_1_2`, then `char_wb_3_5`) and ascending C. Select the preferred SVM scenario using the same validation metrics, preferring `original_only` on an exact remaining scenario tie.

Save `selection_locked.json` before any SVM test scoring. It records input/config hashes, run identity, all candidate settings, the best configuration per scenario, preferred scenario, selection rule, and timestamp. Preserve that record with the final artifacts. This documents the execution sequence; it is not a claim of independent external auditing or of previously unseen test evidence.

Refit fresh pipelines on train + validation, with synthetic examples added only in the augmented scenario. Evaluate the two selected configurations on the same original test set. Do not use test scores to change parameters, thresholds, scenarios, cleaning rules, or labels.

## 5. TF-IDF and SVM settings

Use `Pipeline(TfidfVectorizer, LinearSVC)`. Keep the distinction explicit: TF-IDF encodes text; SVM learns a decision boundary and predicts a label. LinearSVC is the linear support vector classifier implementation used here. [Official LinearSVC documentation](https://scikit-learn.org/1.8/modules/generated/sklearn.svm.LinearSVC.html).

Match the shared TF-IDF candidate settings:

| Setting | Values |
| --- | --- |
| Word representation | `analyzer='word'`, `ngram_range=(1, 2)` |
| Character representation | `analyzer='char_wb'`, `ngram_range=(3, 5)` |
| Shared options | `min_df=2`, `max_features=40000`, `sublinear_tf=True`, `lowercase=False` |
| Explicit matching defaults | `norm='l2'`, `use_idf=True`, `smooth_idf=True` |

Retain the shared word-tokenization behavior. Use the canonical processed text without additional stemming, stopword removal, resampling, or feature selection. Fit vocabulary and IDF only on the candidate's fitting data. Relearn them from development data during final refit. Keep TF-IDF sparse. [Official TF-IDF documentation](https://scikit-learn.org/1.8/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html).

```python
C_VALUES = [0.1, 1.0, 10.0]

LinearSVC(
    C=c_value,
    penalty='l2',
    loss='squared_hinge',
    dual='auto',
    tol=1e-4,
    max_iter=10000,
    class_weight=None,
    fit_intercept=True,
    intercept_scaling=1,
    random_state=42,
)
```

There are **12 candidate fits**: two representations x three C values x two scenarios. Then perform two final selected refits. Record the tuning budget and durations rather than implying that an equal candidate count means equal computational work across methods.

Capture optimizer iterations, convergence warnings, fitting counts, and feature counts. Resolve nonconvergence before test scoring using a documented larger iteration cap and rerun the affected selection stage. Never silently suppress it.

Use default predictions; do not tune a threshold. Save `decision_function` margins with clear score names. They are not calibrated probabilities and must not be directly compared numerically with another classifier's probability outputs.

## 6. Make the method readable

Write the notebook, README explanations, and method notes in Bahasa Indonesia, with descriptive Python identifiers. The intended reader is a teammate who understands the project but may not understand SVM yet.

Use the same visible story throughout:

```text
komentar_processed -> TF-IDF -> SVM -> prediksi label -> evaluasi
```

For each major notebook section, explain its question, input, operation, output, and implication in a short paragraph before the code. Keep code cells focused and show bounded examples instead of large raw dumps. Training/selection code must be inspectable rather than hidden behind one opaque function.

Explain with small examples:

- Why processed text is converted into numeric features.
- What word and character n-grams capture, and how they differ.
- TF, IDF, and the reason vocabulary/IDF are learned from fitting data only.
- A conceptual SVM separating boundary, margin, and the role of C; avoid presenting a two-dimensional sketch as the actual high-dimensional fitted boundary.
- Why train, validation, and test have different jobs.
- Why synthetic comments enter fitting only.
- False positives, false negatives, precision, recall, positive F1, and macro-F1 using the actual confusion matrix after execution.
- What a decision margin means and why it is not a probability.

Any toy example is clearly labeled and excluded from reported experiment scores. Do not invent result values or fill conclusions before running the experiment.

### Notebook sequence

1. Project purpose, method overview, and eventual observed summary.
2. Environment, paths, seed, candidate grid, and shared protocol.
3. Import verification and canonical data checks.
4. Manifest-based partitions and scenario/class-count table.
5. Readable TF-IDF/SVM pipeline and metric definitions.
6. All candidate fits with validation table and F1-versus-C figure.
7. Validation-based selection and saved pre-test selection record.
8. Fresh final refits and test evaluation for both SVM scenarios.
9. Confusion matrices, classification reports, errors, and feature coefficients.
10. Fixed example inference using saved models and shared cleaning.
11. Export, independent verification, and model reload checks.
12. SVM findings, limitations, and handoff instructions for the paper owner.

The notebook reports only the two SVM scenarios. It does not include other classifiers or a cross-method result table.

## 7. Explicit output contract

Document schemas in `docs/KONTRAK_HASIL.md` and version them as `schema_version='1.0'`. Never require the fourth teammate to transcribe graph labels or reverse-engineer a notebook to recover the scores.

### Metrics

`test_metrics.csv` contains exactly two rows, one per SVM scenario, with:

- `run_id`, `method='SVM'`, `classifier='LinearSVC'`, and `scenario`.
- Selected `features` and `C`, `fit_rows`, and `test_rows`.
- `accuracy`, `precision_1`, `recall_1`, `f1_1`, and `macro_f1`.
- `tn`, `fp`, `fn`, and `tp`.
- `refit_seconds` and `test_predict_seconds`.

Store metric values on a 0-1 scale. Use class `1` for positive precision/recall/F1, `zero_division=0`, macro-F1 over labels `[0, 1]`, and confusion-matrix order `[0, 1]`. Display consistent percentages and support counts in the notebook. Save full per-class reports in `classification_reports.json`.

### Record-level evidence

`test_predictions.csv` uses long format: **1,787 rows per scenario, 3,574 rows total**. Required columns are `run_id`, `method`, `scenario`, `source_row`, `split='test'`, `label`, `prediction`, `decision_score`, and `processed_text_sha256`.

The unique key within a run is `(scenario, source_row)`. The record ID, reference label, and processed-text hash must agree with the canonical snapshot for every row. Scenario rows use exactly the same 1,787 original test IDs. The bundle includes the original cleaned snapshot so reviewers can recover source/processed text without relying on a screenshot.

`test_errors.csv` contains all mismatches for both scenarios, with the same identities/scores plus raw/processed comment text and `error_type`. Keep bounded examples in the notebook; do not modify reference labels to make errors disappear.

### Selection, provenance, and models

- `validation_results.csv`: every attempted configuration, validation metrics, fit/sample/feature counts, iteration count, convergence status, and full-pipeline fit duration.
- `selection_locked.json`: the preserved pre-test selection record.
- `experiment_summary.json`: schema/run/config identities, data and manifest hashes, source commit, code revision or source-file hashes when uncommitted, label mapping, class/split counts, full settings, selection policy/results, timing definitions, random seed, Python/library/platform/CPU information, and limitations.
- `selected_model_feature_weights.csv`: preferred SVM feature names and signed coefficients, checked against the fitted vectorizer. They describe fitted associations rather than causal explanations.
- Two `.joblib` pipelines: each contains its fitted TF-IDF and refitted SVM and consumes processed text. `predict.py` provides raw-comment inference by applying `preprocessing.py` first.
- Figures: validation behavior, two confusion matrices, the two SVM scenario metrics, and signed feature coefficients. Include readable labels, units, and sample counts.

Measure full TF-IDF-plus-SVM candidate/refit times, separate from data import and prediction. Record hardware/environment and total tuning time. The paper owner can decide whether timing conditions across methods permit a direct comparison; this repo supplies the measurement definitions without ranking other methods.

## 8. Accountability and reproducibility

**Input integrity:** Import exact bytes; configure CSV attributes to avoid line-ending conversion; record/verify source hashes before and after the experiment. A new dataset version requires a coordinated new contract.

**Training integrity:** Use the fixed partitions and pipeline fitting rules. Preserve all 12 validation results and the selection record, including the chosen parameters and scenario. Keep synthetic examples out of validation/test and metadata out of features.

**Independent result checks:** `scripts/verify_run.py` reads exported predictions and canonical inputs, reconstructs the confusion counts, and independently recomputes accuracy, positive precision/recall/F1, and macro-F1 from those counts. It checks both scenarios, exact ID/label/text-hash membership, error rows, class supports, and reported counts. These checks do not depend on the notebook's metric helper.

**Model checks:** Reload both saved pipelines, reproduce their test predictions, and compare decision margins within an explicit numerical tolerance. Verify feature/coefficient alignment and confirm raw-comment inference uses the same deterministic cleaning as the canonical processed comments.

**Run integrity:** Use a separate run directory with a shared `run_id` and configuration fingerprint. Write completed files through temporary files followed by replacement. Mark a run complete only after every required export/check succeeds. Distinguish partial runs from completed ones; never mix artifacts from different runs.

**Receipts:** `verification.json` records the concrete checks, scope, result, and any unverified item. `artifact_manifest.json` lists artifact paths, byte sizes, and SHA-256 hashes, excluding itself. This establishes traceability and catches mismatched files; it does not prove annotation correctness or establish unseen-source generalization.

**Notebook checks:** Author with `nbformat`, validate structure, run from a fresh Jupyter kernel top-to-bottom, retain execution counts/outputs, and inspect the saved notebook or HTML plus the actual figures. Resolve stale summaries, missing outputs, clipped labels, and unreadable tables before delivery.

**Failure behavior:** Missing dependencies, mismatched data, invalid labels, broken joins, unexpected partitions, unresolved convergence, or failed reconciliation stop the affected stage with a clear reason. Do not fabricate scores, silently alter the experiment, or mark an unexecuted notebook complete.

## 9. Concrete handoff to the fourth teammate

Produce a local `deliverables/svm_<run_id>.zip` with a single clearly identified completed run. Include:

1. A short reading guide, the executed notebook, and SVM method/results notes.
2. Metric CSVs, all validation results, per-class reports, figures, and record-level predictions/errors.
3. Selection/configuration records, provenance, environment versions, and verification/artifact manifests.
4. The exact shared input snapshot and split manifest used in that run.
5. Both saved models and the code/commands needed to verify the scores, repeat inference, and rerun the experiment.

Exclude `.git`, `.venv`, caches, temporary files, unrelated repositories, and partial runs. Verify the archive's required entries and included hashes before delivering it. No external sending or uploading is performed automatically.

The reading order is README -> `METODE_SVM.md` -> executed notebook -> `HASIL_SVM.md` -> `KONTRAK_HASIL.md` and the exported evidence. The fourth teammate can cite actual parameters and copy numeric values from CSVs, trace examples by `source_row`, verify dataset/split identity, and reproduce the reported scores. Their three-method analysis and the complete paper remain outside this repository.

`HASIL_SVM.md` discusses SVM's two training scenarios, observed mistakes, and limitations only. It makes no claims about the other methods' accuracy or superiority.

## 10. Environment and research limits

The currently exposed interpreter is Python 3.11.9 with no scientific/Jupyter packages installed. After approval, create an ignored `.venv` inside `svm-classifier`. Use the shared scientific version baseline where supported: NumPy 2.4.4, pandas 3.0.2, scikit-learn 1.8.0, Matplotlib 3.10.8, and joblib 1.5.3. Include the required Jupyter/kernel/authoring/execution tools and record all resolved versions, including SciPy.

Check installation compatibility explicitly before fitting. Record any necessary version deviation and its implications rather than silently substituting packages. Keep runnable paths relative/configurable and document local VS Code/Jupyter setup. CPU execution is sufficient for this design.

Retain the source limitations: annotation/official class definitions are unconfirmed; deduplication changes frequency prevalence; synthetic comments are authored templates; and near-duplicate templates, site names, videos, or campaigns may cross the random partitions. Scores describe this dataset and split. They do not establish performance on all YouTube comments, new campaigns, or future videos. A documented comparison can be valid even when SVM is not the best-scoring method.

## 11. Implementation order and acceptance criteria

Only after explicit approval:

1. Create the independent `svm-classifier` local repository, descriptive README, environment, and configurations.
2. Implement pinned data import and validation; verify the exact shared snapshot.
3. Write the readable notebook and inference helpers; execute the 12 validation candidates and resolve convergence.
4. Lock selection, refit the two scenarios, evaluate, and export SVM evidence.
5. Run independent artifact/model checks, inspect the executed presentation, and record verification status.
6. Complete the SVM method/results/schema notes and verified handoff archive for the fourth teammate.

Acceptance requires exact shared data/split hashes; documented validation-only selection; the preserved pre-test record; 7,147/8,213 final fitting rows; 1,787 original test predictions per scenario; two metric rows with independently reproducible values; matching errors and supports; saved-model round-trip agreement; a readable freshly executed and visually inspected notebook; a complete verified handoff; and no cross-method evaluation code/results. Athar's tracked repository content remains unchanged.

The user approved implementation, execution, and publication to the public repository aidanismail/svm-classifier on 21 October 2026.
