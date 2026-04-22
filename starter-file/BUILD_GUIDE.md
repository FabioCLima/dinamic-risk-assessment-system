# Dynamic Risk Assessment System — Build & Run Guide (Local + Udacity Workspace)

This project is the Udacity **Dynamic Risk Assessment System** starter codebase. The overall objective is to create, deploy, and monitor an attrition-risk model, and automate retraining/redeployment as new data arrives.

This guide is based on:
- `project_background.txt` (project overview and required workspace locations)
- `step1_data_ingestion.txt` (Step 1: data ingestion requirements)

## 1) Project layout (expected)

In both **local development** and the **Udacity Workspace**, keep the following structure at your project root (the same folder that contains `config.json`):

```
.
├── config.json
├── ingestion.py
├── training.py
├── scoring.py
├── deployment.py
├── diagnostics.py
├── reporting.py
├── app.py
├── apicalls.py
├── fullprocess.py
├── wsgi.py
├── requirements.txt
├── practicedata/                 # practice input data (dataset1.csv, dataset2.csv)
├── sourcedata/                   # source input data (dataset3.csv, dataset4.csv)
├── testdata/                     # test dataset (testdata.csv)
├── ingesteddata/                 # Step 1 outputs (finaldata.csv, ingestedfiles.txt)
├── practicemodels/               # practice model artifacts (starter config)
├── models/                       # production model artifacts (final config)
└── production_deployment/        # deployed artifacts for the API
```

Notes:
- `config.json` controls where each script reads/writes.
- The Udacity Workspace also uses `/home/workspace` as the typical project root directory.

## 2) Step 1 (Data ingestion): what you must implement

Per `step1_data_ingestion.txt`, `ingestion.py` must:
1. **Auto-detect** every `.csv` file inside the folder specified by `input_folder_path` in `config.json` (no hard-coded filenames).
2. Load and **combine** them into a single Pandas DataFrame.
3. **De-duplicate** rows.
4. Save the merged dataset as `finaldata.csv` inside `output_folder_path`.
5. Save a record of ingested files as `ingestedfiles.txt` inside `output_folder_path`.

In this repo, `starter-file/ingestion.py` already implements these requirements and writes:
- `ingesteddata/finaldata.csv`
- `ingesteddata/ingestedfiles.txt` (one filename per line)

## 3) Build & run locally (this repository)

### 3.1 Create/activate a Python environment

From this repo, your project root is:

`/home/fabiolima/Desktop/MLOps_Projects/Dinamic_Risk_Assessment_System/starter-file`

Run:

```bash
cd /home/fabiolima/Desktop/MLOps_Projects/Dinamic_Risk_Assessment_System/starter-file

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you have Python version conflicts with the pinned dependencies in `requirements.txt`, use a Python version close to what Udacity provides (commonly Python 3.8/3.9).

### 3.2 Run Step 1 ingestion

```bash
cd /home/fabiolima/Desktop/MLOps_Projects/Dinamic_Risk_Assessment_System/starter-file
python ingestion.py
```

Verify outputs:

```bash
ls -la ingesteddata/
head -n 5 ingesteddata/finaldata.csv
cat ingesteddata/ingestedfiles.txt
```

### 3.3 Switch from “practice” to “production” paths (later in the project)

The starter `config.json` uses practice locations:
- `input_folder_path: practicedata`
- `output_model_path: practicemodels`

When you are ready to finalize the full project, update `config.json` to use:
- `input_folder_path: sourcedata`
- `output_model_path: models`

Keep `output_folder_path: ingesteddata` unless you explicitly want a different ingestion output folder.

## 4) Build & run in the Udacity Workspace

### 4.1 Create the project in the Workspace

In Udacity, you typically work under:
- `/home/workspace`

Create a project folder (name is up to you):

```bash
mkdir -p /home/workspace/dynamic_risk_assessment
cd /home/workspace/dynamic_risk_assessment
```

### 4.2 Copy the starter code into the Workspace

You have two common options:

**Option A — Upload files via the Udacity file browser**
- Upload the contents of this repo’s `starter-file/` into `/home/workspace/dynamic_risk_assessment/`.
- Ensure `config.json` sits at the project root (same folder as `ingestion.py`).

**Option B — Zip locally and upload the zip**
1. Locally, create a zip of the `starter-file/` contents.
2. Upload it in the Workspace, then unzip it in `/home/workspace/dynamic_risk_assessment/`.

After copying, confirm the expected files exist:

```bash
ls -la
cat config.json
```

### 4.3 Install dependencies

From the project root:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Run Step 1 ingestion (Workspace)

```bash
python ingestion.py
ls -la ingesteddata/
```

You should see:
- `ingesteddata/finaldata.csv`
- `ingesteddata/ingestedfiles.txt`

## 5) What’s next (Steps 2–5)

The starter includes scripts for the remaining steps:
- Step 2: `training.py`, `scoring.py`, `deployment.py`
- Step 3: `diagnostics.py`
- Step 4: `reporting.py`, `app.py`, `apicalls.py`, `wsgi.py`
- Step 5: `fullprocess.py` (automation orchestration)

Those files are templates in the starter and will be completed in later steps of the project.
