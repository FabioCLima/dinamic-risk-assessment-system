# Step 2 — Training, Scoring, and Deploying the ML Model (Architecture Guide)

This guide explains **how to design and implement Step 2** of the Udacity *Dynamic Risk Assessment System* project using the provided starter codebase.

Step 2 produces three core artifacts:

- A trained model: `trainedmodel.pkl`
- A model score report: `latestscore.txt` (F1 score)
- A “production deployment” bundle: copies of `trainedmodel.pkl`, `latestscore.txt`, and `ingestedfiles.txt`

The work is implemented in these starter scripts:

- `training.py` (train model)
- `scoring.py` (score model)
- `deployment.py` (deploy/copy artifacts to production folder)

---

## 1) Prerequisites (Step 1 output contract)

Step 2 depends on Step 1’s ingestion outputs in `output_folder_path` (from `config.json`):

- `finaldata.csv` (training dataset)
- `ingestedfiles.txt` (record of ingested input CSV filenames)

**You should run Step 1 before Step 2.**

### Data contract (`finaldata.csv`)

`finaldata.csv` has 5 columns:

- `corporation` (string identifier; **do not use** as a feature)
- `lastmonth_activity` (numeric feature)
- `lastyear_activity` (numeric feature)
- `number_of_employees` (numeric feature)
- `exited` (target label; 0/1)

Feature set used across training + scoring must be consistent:

```text
FEATURES = ["lastmonth_activity", "lastyear_activity", "number_of_employees"]
TARGET   = "exited"
DROP     = ["corporation"]
```

---

## 2) Configuration-driven architecture (no hard-coded paths)

All scripts must load `config.json` and derive paths from it:

Key entries:

- `output_folder_path`: where Step 1 wrote `finaldata.csv` and `ingestedfiles.txt`
- `test_data_path`: where `testdata.csv` lives
- `output_model_path`: where Step 2 writes model artifacts (`trainedmodel.pkl`, `latestscore.txt`)
- `prod_deployment_path`: where deployment copies production-ready artifacts

**Best practice:** treat the folder containing `config.json` as the **project root**, and build all paths relative to it. This makes the code portable between local execution and Udacity Workspace.

---

## 3) Step 2.1 — Model Training (`training.py`)

### Responsibilities

`training.py` should implement a single public function (called by the CLI entrypoint and reusable by automation later):

- `train_model() -> <trained model or path>`

The training function must:

1. Read `finaldata.csv` from `output_folder_path`
2. Train a `sklearn.linear_model.LogisticRegression` model using the 3 numeric features
3. Serialize the trained model to `trainedmodel.pkl` in `output_model_path`

### Recommended structure

**Inputs**

- `finaldata.csv` (from `output_folder_path`)

**Outputs**

- `trainedmodel.pkl` (to `output_model_path`)

**Core steps**

1. Load config + resolve directories
2. Read CSV with Pandas
3. Select `X` and `y`
4. Train logistic regression
5. Ensure output directory exists
6. Write `trainedmodel.pkl` (pickle)

### Software-engineering practices

- Use type hints and docstrings for functions.
- Use `pathlib.Path` for path handling.
- Validate input file exists; raise clear exceptions if not.
- Make training deterministic by setting `random_state` (and any other relevant parameters).
- Avoid global side effects during import; put execution under `if __name__ == "__main__":`.
- Keep training code narrowly scoped: don’t mix scoring/deployment here.

---

## 4) Step 2.2 — Model Scoring (`scoring.py`)

### Responsibilities

`scoring.py` should implement:

- `score_model() -> float`

The scoring function must:

1. Read **test data** from `test_data_path` (usually `testdata/testdata.csv`)
2. Read the trained model from `output_model_path/trainedmodel.pkl`
3. Compute an **F1 score** against the test labels
4. Write the score to `output_model_path/latestscore.txt`

### Recommended structure

**Inputs**

- `testdata.csv` (from `test_data_path`)
- `trainedmodel.pkl` (from `output_model_path`)

**Outputs**

- `latestscore.txt` (to `output_model_path`)

**Core steps**

1. Load config + resolve directories
2. Read test CSV
3. Load model (pickle)
4. Predict on test features
5. Compute `sklearn.metrics.f1_score(y_true, y_pred)`
6. Write to `latestscore.txt` as a single number (e.g. `0.63`)

### Software-engineering practices

- Centralize feature selection so it matches training exactly.
- Fail fast if model file is missing (common when training wasn’t run).
- Make `latestscore.txt` writing robust and simple:
  - single line
  - newline at the end
- Return the score from `score_model()` so other scripts can reuse it without re-reading the file.

---

## 5) Step 2.3 — Deployment (`deployment.py`)

### Responsibilities

Deployment **does not create new artifacts**; it copies existing ones into the production deployment directory.

`deployment.py` should implement:

- `store_model_into_pickle(model: Optional[object] = None) -> None`

Required copy operations into `prod_deployment_path`:

1. `trainedmodel.pkl` (from `output_model_path`)
2. `latestscore.txt` (from `output_model_path`)
3. `ingestedfiles.txt` (from `output_folder_path`)

### Recommended structure

**Inputs**

- `trainedmodel.pkl`
- `latestscore.txt`
- `ingestedfiles.txt`

**Outputs**

- Copies of all three in `prod_deployment_path/`

**Core steps**

1. Load config + resolve directories
2. Ensure `prod_deployment_path` exists
3. Verify source files exist
4. Copy using `shutil.copy2` (preserves timestamps/metadata)

### Software-engineering practices

- Treat deployment as idempotent: re-running should safely overwrite the same filenames.
- Copy from known sources derived from `config.json` only (no hard-coded absolute paths).
- Keep the deployment function pure “copy only” to simplify debugging and later automation (`fullprocess.py`).

---

## 6) Execution flow (how Step 2 should be run)

Minimum flow:

1. Run Step 1 ingestion (creates `finaldata.csv` + `ingestedfiles.txt`)
2. Run training (creates `trainedmodel.pkl`)
3. Run scoring (creates `latestscore.txt`)
4. Run deployment (copies the three artifacts to `production_deployment/`)

Example commands (from the project root that contains `config.json`):

```bash
python ingestion.py
python training.py
python scoring.py
python deployment.py
```

---

## 7) “Practice” vs “Production” configuration

The starter `config.json` commonly points to practice paths:

- `input_folder_path: practicedata`
- `output_model_path: practicemodels`

When finalizing the project you usually switch to:

- `input_folder_path: sourcedata`
- `output_model_path: models`

This guide’s design remains the same; only the paths in `config.json` change.

---

## 8) Validation checklist (what “done” looks like)

After running Step 2, you should have:

Under `output_model_path/`:

- `trainedmodel.pkl`
- `latestscore.txt`

Under `prod_deployment_path/`:

- `trainedmodel.pkl`
- `latestscore.txt`
- `ingestedfiles.txt`

Sanity checks:

- `latestscore.txt` contains a single float-like number
- The deployed directory contains the latest versions (timestamps update after redeploy)

