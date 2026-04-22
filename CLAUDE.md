# CLAUDE.md

Guidance for Claude Code when working inside this repository. Read this before touching code.

## What this repository is

Udacity **Dynamic Risk Assessment System** — a batch MLOps pipeline that ingests data,
trains/scores/deploys a logistic regression attrition-risk model, runs diagnostics,
exposes a Flask API, and automates re-training/re-deployment via cron.

The repository has three top-level folders:

- `docs/` — the original project spec (`project_background.md`, `step1`…`step5.md`,
  `standout_suggestion_optional.md`). **This is the source of truth for requirements.**
- `starter-file/` — reference starter scripts (read-only, Udacity template).
- `workspace_local/` — **the working implementation.** All development happens here.

## Working directory

All commands below assume you are inside `workspace_local/`:

```bash
cd /home/fabiolima/Desktop/MLOps_Projects/Dinamic_Risk_Assessment_System/workspace_local
```

The scripts resolve paths relative to `Path(__file__).resolve().parent`, so they can
be invoked from anywhere as long as this folder holds `config.json` next to the `.py`
files.

## Environment

- Python: **3.9.x** (pinned in `.python-version`, enforced by `pyproject.toml`).
- Virtualenv: `.venv/` (created with `uv venv`).
- Dependencies: `requirements.txt` (pinned to old versions for Udacity compatibility).
- Package manager: `uv` (preferred) or `pip` inside the venv.

Bootstrap:

```bash
uv venv --python 3.9
source .venv/bin/activate
uv pip install -r requirements.txt
uv pip install pytest pytest-cov          # dev-only, not in requirements.txt
```

Always invoke Python through the venv: `.venv/bin/python <script>.py`.

## How the pipeline is wired

`config.json` is the single switchboard — no paths are hard-coded in code:

| Key | Current value | Purpose |
|---|---|---|
| `input_folder_path` | `sourcedata` | Where ingestion reads CSVs |
| `output_folder_path` | `ingesteddata` | Where `finaldata.csv` + `ingestedfiles.txt` land |
| `test_data_path` | `testdata` | Where `testdata.csv` lives |
| `output_model_path` | `models` | Where `trainedmodel.pkl`, `latestscore.txt`, plots, and `apireturns.txt` land |
| `prod_deployment_path` | `production_deployment` | The "deployed" artifacts copied by `deployment.py` |

Switching between practice and final modes is a **config change only**:
`input_folder_path: practicedata → sourcedata`, `output_model_path: practicemodels → models`.

## Steps and entry points

| Step | Script | Key function | Writes |
|---|---|---|---|
| 1 Ingestion | `ingestion.py` | `merge_multiple_dataframe()` | `ingesteddata/finaldata.csv`, `ingesteddata/ingestedfiles.txt` |
| 2 Training | `training.py` | `train_model()` | `models/trainedmodel.pkl` |
| 2 Scoring | `scoring.py` | `score_model()` | `models/latestscore.txt` |
| 2 Deploy | `deployment.py` | `store_model_into_pickle()` | Copies the three artifacts into `production_deployment/` |
| 3 Diagnostics | `diagnostics.py` | `model_predictions`, `dataframe_summary` (mean/median/**mode**), `missing_data`, `execution_time`, `outdated_packages_list` | — |
| 4 Reporting | `reporting.py` | `generate_confusion_matrix_plot()`, `generate_pdf_report()` | `models/confusionmatrix.png`, `models/report.pdf` |
| 4 API | `app.py` (factory `create_app()`) + `wsgi.py` | `/prediction`, `/scoring`, `/summarystats`, `/diagnostics` | HTTP responses |
| 4 API client | `apicalls.py` | `call_api_endpoints`, `write_api_returns` | `models/apireturns.txt` |
| 5 Orchestrator | `fullprocess.py` | `run_full_process(force, archive)` | `models/confusionmatrix2.png`, `models/apireturns2.txt` |
| 5 Cron | `cronjob.txt` | — | Runs `fullprocess.py` every 10 min |
| Standout 1 | `reporting.py --pdf` | `generate_pdf_report()` (reportlab) | `models/report.pdf` |
| Standout 2 | `archive_diagnostics.py` / triggered by `fullprocess.py` | `archive_current_diagnostics()` | `olddiagnostics/*_<UTCstamp>.{txt,csv,png}` |
| Standout 3 | `dbsetup.py` (auto-invoked by ingestion/scoring/diagnostics) | `init_db`, `record_ingestion`, `record_score`, `record_diagnostics` | `ingesteddata/pipeline_history.sqlite` |

All entry points accept `--help` (argparse). Useful flags:
- `app.py --host 127.0.0.1 --port 8765 [--debug]`
- `apicalls.py --port 8765 --prediction-input testdata/testdata.csv --output apireturns.txt`
- `fullprocess.py --no-archive`
- `reporting.py --output confusionmatrix.png --pdf [report.pdf]`
- `diagnostics.py --skip-timing --skip-deps`

## Run the pipeline end-to-end

```bash
.venv/bin/python ingestion.py
.venv/bin/python training.py
.venv/bin/python scoring.py
.venv/bin/python deployment.py
.venv/bin/python reporting.py
.venv/bin/python apicalls.py        # spawns app.py locally if not running
.venv/bin/python fullprocess.py     # idempotent; exits early if no new data
```

Expose the API manually (optional):

```bash
APP_PORT=8000 .venv/bin/python app.py
# or production-style:
.venv/bin/gunicorn --bind 0.0.0.0:8000 wsgi:app
```

## Testing

Tests live in `workspace_local/tests/` and are run with pytest:

```bash
.venv/bin/pytest                    # run all tests
.venv/bin/pytest tests/test_ingestion.py -v
.venv/bin/pytest --cov=. --cov-report=term-missing
```

Conventions:
- Each step has a `tests/test_<step>.py` module.
- Tests that touch disk use `tmp_path` + a helper that builds a minimal `config.json`
  and synthetic CSVs, then monkey-patches the script's `_get_project_dir` (or the
  module's working dir) to point there. This keeps tests hermetic and avoids
  clobbering real `ingesteddata/` / `models/` outputs.
- Tests that depend on network / `pip list --outdated` are marked `@pytest.mark.slow`
  and skipped by default.
- Fast-path default: `pytest` completes in under ~30s.

## Coding conventions (enforced in review)

- **Config-driven paths only.** Never hard-code `/home/workspace`, `./ingesteddata`,
  etc. Always resolve through `config.json`.
- **`pathlib.Path` everywhere**; no `os.path.join` / raw string paths.
- **Logging, not `print`.** Use `logger = logging.getLogger(__name__)` and set up
  `basicConfig` only in the script's `main()`.
- **Module-level constants** for feature/target names (`FEATURE_COLUMNS`, `TARGET_COLUMN`).
- **Explicit FileNotFoundError / ValueError** with actionable messages at every I/O
  boundary. Do not swallow errors.
- **Idempotent writes.** Running the same script twice must produce the same artifacts.
- **No `from __future__ import annotations`** (flagged in `project_design.md` as a
  compatibility risk with the Udacity grader).
- **Typed function signatures** (PEP 484). Return types matter — the spec requires
  `list`/`DataFrame` shapes.
- **Docstrings** on every public function, documenting the contract (reads/writes).

## Non-negotiable contracts from the spec

- `ingestion.py` **must** auto-discover `*.csv`; no hard-coded filenames.
- `scoring.py` **must** write a single-float-per-line `latestscore.txt`.
- `deployment.py` **must only copy** — no training or scoring.
- `diagnostics.execution_time()` returns `[ingestion_seconds, training_seconds]` —
  two floats, in that order.
- `diagnostics.missing_data()` returns one percent per column, in column order.
- `diagnostics.model_predictions(df)` uses the **deployed** model
  (`prod_deployment_path`), not the one in `output_model_path`.
- All four API endpoints must return HTTP 200 — even on error responses.
- `fullprocess.py` must no-op when no new CSVs appeared since the last ingestion.

## Deploy gate (rubric, Section 5)

- `fullprocess.py` must deploy **only** when (a) new CSVs appeared since the last
  ingestion AND (b) the candidate model's F1 is strictly greater than the deployed
  model's F1 (`candidate_score > deployed_score`). If no deployed score exists yet,
  treat as initial deployment.
- Score equal to or worse than deployed → no redeploy.

## Files never to edit

- `docs/**` — spec, read-only reference.
- `starter-file/**` — Udacity template, read-only reference.
- `workspace_local/sourcedata/`, `practicedata/`, `testdata/` — fixture data.

## Useful pointers

- Architecture notes: `workspace_local/project_design.md`
- Build & run guide (starter-oriented): `starter-file/BUILD_GUIDE.md`
- Step specs: `docs/step1_data_ingestion.md` … `docs/step5_process_automation.md`
