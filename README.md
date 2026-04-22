# Dynamic Risk Assessment System

An end-to-end MLOps project that predicts customer attrition risk and automates model monitoring and redeployment.

This repository is structured to be readable by both:
- non-technical readers (recruiters, stakeholders, hiring managers)
- technical readers (data scientists, ML engineers, software engineers)

---

## What this project does (plain language)

Companies lose customers over time. This project helps identify which customers are at higher risk of leaving, so teams can act early.

In simple terms, the system:
1. Collects new data files
2. Trains a machine learning model
3. Measures if the model is good enough
4. Publishes the model for use
5. Exposes results through an API
6. Rechecks performance automatically when new data arrives

---

## Why this matters for data scientists

Many portfolios show only model training in a notebook. Real-world work usually requires more:
- repeatable data pipelines
- model performance tracking
- deployment logic and safety checks
- operational diagnostics
- automated re-training workflows

This project demonstrates those operational skills, not only model experimentation.

---

## Current implementation status

The portfolio-native implementation now lives in `src/dynamic_risk_assessment/`.
The `workspace_local/` scripts are preserved as **legacy compatibility wrappers**.

It already includes:
- ingestion, training, scoring, deployment, diagnostics, reporting
- Flask API endpoints
- process automation (`fullprocess.py`)
- tests and optional standout features (PDF reporting, diagnostics archive, SQLite history)

---

## Repository orientation

- `src/portfolio_pipeline/` — root-level portfolio CLI wrapper
- `configs/` — config profiles for current and future layout
- `reports/` — model card and monitoring templates
- `notebooks/` — analysis notebook roadmap
- `workspace_local/` — working implementation (source of executable pipeline)
- `docs/` — architecture and portfolio-oriented documentation
- `submission/` — packaging used for course submission
- `starter-file/` — original starter material

As the next step, we can progressively promote `workspace_local/` modules to a cleaner root-level `src/` layout for a public portfolio version.

---

## Fast technical walkthrough

Inside `workspace_local/`, the baseline flow is:

1. `ingestion.py` -> creates merged dataset
2. `training.py` -> trains logistic regression model
3. `scoring.py` -> computes F1 score
4. `deployment.py` -> copies approved artifacts to production folder
5. `reporting.py` -> generates confusion matrix and report artifacts
6. `app.py` + `apicalls.py` -> serves and consumes API diagnostics
7. `fullprocess.py` -> automates checks and conditional redeploy

---

## Run from repository root

You can now run the existing pipeline from the repository root through the portfolio CLI:

```bash
pip install -e .
dras run-all
```

Or run individual steps:

```bash
dras run-step --name ingestion
dras run-step --name training
dras run-step --name scoring
```

The CLI now executes native modules in `src/dynamic_risk_assessment/`.
By default, config is loaded from root `config.json` (or `configs/config.dev.json` fallback).
You can override config profile with:

```bash
DRAS_CONFIG=configs/config.dev.json dras run-all
```

---

## Portfolio roadmap

1. Root portfolio scaffolding (`src/`, `configs/`, `reports/`, `notebooks/`) - completed
2. Root execution entrypoint (`dras` CLI + `Makefile`) - completed
3. Root CI pipeline (`.github/workflows/ci.yml`) - completed
4. Root docs (`docs/architecture.md`, `docs/api.md`, `docs/PORTFOLIO_OVERVIEW.md`) - completed
5. Full module migration from `workspace_local/` to `src/` - completed

---

## Portfolio completion checklist

- [x] Non-technical and technical overview at repository root
- [x] Root project packaging and command-line entrypoint
- [x] Recruiter-friendly architecture and business-value documentation
- [x] Model card and monitoring templates
- [x] Root test scaffold and CI workflow
- [x] Native `src/` implementation replacing `workspace_local/` scripts
- [ ] Public GitHub repository setup and first release

---

## Notes

- You do not need a GitHub repo yet to improve project structure and storytelling.
- Once you are ready, we can prepare a clean first public commit sequence optimized for recruiter review.
