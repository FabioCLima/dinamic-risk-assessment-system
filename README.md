# Dynamic Risk Assessment System

[![CI](https://github.com/FabioCLima/dinamic-risk-assessment-system/actions/workflows/ci.yml/badge.svg)](https://github.com/FabioCLima/dinamic-risk-assessment-system/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![scikit-learn](https://img.shields.io/badge/scikit--learn-0.24%2B-orange)
![Flask](https://img.shields.io/badge/Flask-1.1%2B-lightgrey)

An end-to-end MLOps pipeline that predicts customer attrition risk, automates model monitoring, and re-deploys only when a better model is found.

This repository is structured to be readable by both:
- **Non-technical readers** (recruiters, stakeholders, hiring managers)
- **Technical readers** (data scientists, ML engineers, software engineers)

---

## What this project does (plain language)

Companies lose customers over time. This system identifies which customers are at higher risk of leaving so that teams can act early.

The system runs automatically on a schedule and:
1. Detects new data files
2. Trains a machine learning model on the latest data
3. Compares the new model against what is already in production
4. Deploys the new model **only if it performs better**
5. Exposes results and diagnostics through a REST API
6. Logs everything for traceability

---

## Why this project matters

Most portfolios show model training in a notebook. Real-world ML engineering requires more:

| Skill | How it appears here |
|---|---|
| Repeatable data pipelines | `ingestion.py` auto-discovers and merges CSVs |
| Performance tracking | F1 score logged and compared at every run |
| Safe deployment | Candidate model replaces production only when `candidate_F1 > deployed_F1` |
| Operational diagnostics | Summary stats, missingness %, timing, dependency audit |
| API delivery | Flask endpoints for predictions, scoring, stats, diagnostics |
| Automated re-training | `fullprocess.py` orchestrates the full cycle via cron |
| Testing | Hermetic pytest suite covering each pipeline step |
| CI/CD | GitHub Actions runs on every push |

---

## Tech stack

| Layer | Tool |
|---|---|
| Language | Python 3.9+ |
| ML | scikit-learn (LogisticRegression) |
| Data | pandas |
| API | Flask + gunicorn |
| Reporting | matplotlib, seaborn, reportlab (PDF) |
| Persistence | SQLite (run history) |
| Testing | pytest |
| CI | GitHub Actions |
| Packaging | setuptools / pip |

---

## Repository structure

```
.
├── src/
│   ├── dynamic_risk_assessment/   # Pipeline modules (ingestion → fullprocess) + Flask API
│   └── portfolio_pipeline/        # Root-level CLI (dras command)
├── workspace/                     # Data workspace
│   ├── sourcedata/                # Input CSVs
│   ├── testdata/                  # Held-out evaluation data
│   ├── ingesteddata/              # Generated: merged datasets (created by pipeline)
│   ├── models/                    # Generated: trained model artifacts
│   └── production_deployment/     # Generated: deployed artifacts
├── configs/                       # Config profiles (dev, prod)
├── docs/                          # Architecture, API, and project docs
├── reports/                       # Model card and monitoring templates
├── tests/                         # Test suite
├── config.json                    # Active config (points to workspace/ folders)
├── Makefile                       # Convenience targets
└── .github/workflows/ci.yml       # CI pipeline
```

---

## Pipeline overview

```
New CSV files
     │
     ▼
ingestion.py ──► finaldata.csv
     │
     ▼
training.py ──► trainedmodel.pkl
     │
     ▼
scoring.py ──► latestscore.txt (F1)
     │
     ▼
 ┌── fullprocess.py ──────────────────────────────┐
 │   candidate_F1 > deployed_F1 ?                 │
 │   YES → deployment.py → reporting.py → API     │
 │   NO  → keep current deployment                │
 └────────────────────────────────────────────────┘
     │
     ▼
app.py (Flask API)
  POST /prediction
  GET  /scoring
  GET  /summarystats
  GET  /diagnostics
```

---

## Quick start

### Install

```bash
git clone https://github.com/FabioCLima/dinamic-risk-assessment-system.git
cd dinamic-risk-assessment-system
pip install -e .
```

### Run the full pipeline

```bash
dras run-all
```

### Run individual steps

```bash
dras run-step --name ingestion
dras run-step --name training
dras run-step --name scoring
```

### Override config profile

```bash
DRAS_CONFIG=configs/config.dev.json dras run-all
```

### Expose the API

```bash
python -m dynamic_risk_assessment.app --port 8000
```

### Example API calls

```bash
# Get predictions
curl -X POST http://127.0.0.1:8000/prediction \
  -H "Content-Type: application/json" \
  -d '{"filepath": "testdata/testdata.csv"}'

# Get current F1 score
curl http://127.0.0.1:8000/scoring

# Get diagnostics
curl http://127.0.0.1:8000/diagnostics
```

---

## Run tests

```bash
pytest -q
```

---

## Automation via cron

The system is designed to run the full process on a schedule. Example cron entry (every 10 minutes):

```
*/10 * * * * cd /path/to/repo && /path/to/python -m dynamic_risk_assessment.fullprocess
```

The orchestrator is idempotent: it exits immediately if no new data files have arrived since the last ingestion run.

---

## Deployment gate (key design decision)

The system only replaces the production model when **both** conditions are true:

1. New CSV files were detected since the last ingestion
2. The newly trained model's F1 score **strictly exceeds** the deployed model's F1 score

This prevents automatic deployment of a model that is equal to or worse than what is currently in production.

---

## Documentation

- [Architecture](docs/architecture.md) — system design and flow diagrams
- [API reference](docs/api.md) — endpoint descriptions and example calls
- [Model card](reports/model_card.md) — model metadata and performance context

---

## Project background

The problem statement originates from the Udacity ML DevOps Engineer program; this implementation extends it well beyond the original scope with SQLite run history, PDF reporting, diagnostics archiving, config profiles, a packaged CLI (`dras`), and CI.
