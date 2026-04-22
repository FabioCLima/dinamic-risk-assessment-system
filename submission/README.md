# Dynamic Risk Assessment System

This submission contains a complete MLOps pipeline for the Udacity Dynamic Risk Assessment project. Since I developed the project on my own machine, I have included the instructions and all required files.

---

## Resubmission note (addressed reviewer feedback)

Two rubric criteria in **Section 5 — Process Automation** were corrected after the first review:

### 1. Deploy gate now requires strictly better model (Criterion 5.1)

`fullprocess.py` previously deployed whenever the F1 score changed at all (equal **or** different). This could replace a good deployed model with a worse one.

The gate is now aligned with the rubric:

```python
# Old (incorrect): deployed on any difference
drift_detected = abs(new_score - deployed_score) > 1e-12

# New (correct): deploy only when candidate strictly improves F1
should_deploy = (deployed_score is None) or (candidate_score > deployed_score)
```

### 2. Deployment only when both conditions are true (Criterion 5.2)

`fullprocess.py` now follows the exact sequence prescribed by the rubric:

1. **Stop immediately** if no new (non-ingested) CSV files are found in `input_folder_path`.
2. Ingest + retrain + score a candidate model **only** when new data is present.
3. Read the deployed baseline score from `production_deployment/latestscore.txt`.
4. Call `deployment.py` **only** when `candidate_score > deployed_score` (or no deployed score exists — initial deployment).
5. Generate `confusionmatrix2.png` and `apireturns2.txt` **only after** a successful deploy.

The `--force` flag (which bypassed the new-data check) has been removed.

---

## Files included

Every artifact required by the rubric is present:

| File | Step | Description |
|---|---|---|
| `ingestion.py` | 1 | Auto-discover + merge + deduplicate CSVs |
| `training.py` | 2 | Train LogisticRegression, save `trainedmodel.pkl` |
| `scoring.py` | 2 | Compute F1, write `latestscore.txt` |
| `deployment.py` | 2 | Copy 3 artifacts to `prod_deployment_path` |
| `diagnostics.py` | 3 | Predictions, stats, NA %, timing, deps |
| `reporting.py` | 4 | Confusion matrix PNG + optional PDF |
| `app.py` | 4 | Flask API (4 endpoints) |
| `apicalls.py` | 4 | Call all endpoints, save `apireturns.txt` |
| `fullprocess.py` | 5 | End-to-end orchestrator (corrected gate) |
| `finaldata.csv` | artifact | Merged deduplicated training data |
| `ingestedfiles.txt` | artifact | List of ingested CSV filenames |
| `trainedmodel.pkl` | artifact | Trained logistic regression model |
| `latestscore.txt` | artifact | F1 score (single float) |
| `confusionmatrix.png` | artifact | Confusion matrix — initial run |
| `confusionmatrix2.png` | artifact | Confusion matrix — after Step 5 redeploy |
| `apireturns.txt` | artifact | Combined API responses — initial run |
| `apireturns2.txt` | artifact | Combined API responses — after Step 5 redeploy |
| `cronjob.txt` | cron | Runs `fullprocess.py` every 10 minutes |
| `config.json` | config | Path switchboard |
| `requirements.txt` | config | Pinned dependency versions |
| `wsgi.py` | helper | Gunicorn entry point |

Optional standout artifacts are in `standout/`:

| File | Description |
|---|---|
| `archive_diagnostics.py` | Copies diagnostic artifacts with UTC timestamp before each run |
| `dbsetup.py` | SQLite history of ingestion runs, scores, diagnostics |
| `report.pdf` | PDF report (confusion matrix, F1, stats, deps) |
| `pipeline_history.sqlite` | Populated SQLite database |
| `olddiagnostics/` | Timestamped diagnostic snapshots |

---

## Project structure (`config.json`)

```json
{
  "input_folder_path": "sourcedata",
  "output_folder_path": "ingesteddata",
  "test_data_path": "testdata",
  "output_model_path": "models",
  "prod_deployment_path": "production_deployment"
}
```

All scripts resolve paths through `config.json` — no hard-coded paths anywhere.

---

## Setup

### Option 1 — `uv`

```bash
uv venv --python 3.9 .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### Option 2 — standard `venv`

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## How to run the pipeline

```bash
# Step 1 — Ingestion
python ingestion.py

# Step 2 — Train, score, deploy
python training.py
python scoring.py
python deployment.py

# Step 3 — Diagnostics
python diagnostics.py

# Step 4 — Reporting + API
python reporting.py
python app.py --host 0.0.0.0 --port 8001
# (in a second terminal)
python apicalls.py --host 127.0.0.1 --port 8001 --prediction-input testdata/testdata.csv

# Step 5 — Automation (run after new data arrives in sourcedata/)
python fullprocess.py
```

Optional PDF report:

```bash
python reporting.py --pdf
```

### Cron job

```
*/10 * * * * cd /path/to/project && /usr/bin/python3 fullprocess.py
```

Install with `crontab cronjob.txt`.

---

## `fullprocess.py` decision logic (rubric §5)

```
sourcedata/ CSVs  ──▶  already in production_deployment/ingestedfiles.txt?
                              │
                          YES │ NO
                              │  └─▶ ingest → train → score candidate model
                              │              │
                           return           read deployed F1 from
                           (no-op)          production_deployment/latestscore.txt
                                                    │
                                       candidate_score > deployed_score?
                                       (or no deployed score yet?)
                                                    │
                                               NO   │  YES
                                                    │   └─▶ deployment.py
                                               return       confusionmatrix2.png
                                               (no-op)      apireturns2.txt
```

---

## API endpoints

| Method | Path | Returns |
|---|---|---|
| POST | `/prediction` | `{"predictions": [...]}` |
| GET | `/scoring` | `{"f1_score": <float>}` |
| GET | `/summarystats` | `{"summary_statistics": [...]}` |
| GET | `/diagnostics` | `{"timing_seconds": [...], "missing_data_percent": [...], "dependencies": [...]}` |

All endpoints return HTTP 200 (per rubric specification).

---

## Notes for the reviewer

- The standalone scripts support CLI arguments via `argparse` but use sensible defaults when run without flags.
- `fullprocess.py` will archive existing diagnostic artifacts only when `archive_diagnostics` is available (included under `standout/`). Disable with `python fullprocess.py --no-archive`.
- If running locally, ensure the standard Udacity data folders (`practicedata/`, `sourcedata/`, `testdata/`) are present beside the scripts.
- The `standout/` folder contains optional enhancements and can be ignored for base rubric grading.
