# Project Overview

## Background

Imagine that you’re the Chief Data Scientist at a big company with **10,000 corporate clients**. The company is extremely concerned about **attrition risk**: the risk that some clients will exit their contracts and reduce the company’s revenue.

The company has a team of client managers who stay in contact with clients and try to convince them not to exit. However, the team is small, so they can’t stay in close contact with all 10,000 clients.

Your task is to **create, deploy, and monitor** a risk assessment ML model that estimates attrition risk for each client. If the deployed model is accurate, client managers can focus on the highest-risk clients to avoid losing revenue.

This work doesn’t stop at deployment. The industry is dynamic; a model trained a year or even a month ago may no longer be accurate. Because of this, you must set up **regular monitoring** and processes/scripts to:

- re-train
- re-deploy
- monitor
- report

so the company always has the most accurate risk assessments possible.

## Project steps overview

You’ll complete the project in **5 steps**:

1. **Data ingestion**
   - Automatically check a database for new data usable for model training.
   - Compile all training data into a training dataset and save it to persistent storage.
   - Write ingestion metrics to persistent storage.
2. **Training, scoring, and deploying**
   - Train an ML model that predicts attrition risk.
   - Score the model.
   - Save the model and scoring metrics to persistent storage.
3. **Diagnostics**
   - Determine and save summary statistics for a dataset.
   - Time performance of training and scoring scripts.
   - Check for dependency changes and package updates.
4. **Reporting**
   - Automatically generate plots/documents reporting model metrics.
   - Provide an API endpoint that returns model predictions and metrics.
5. **Process automation**
   - Create a script and cron job that automatically runs all previous steps at regular intervals.

## Project submission

You will submit a **zip file** containing all scripts required for the project. The zip will also include Step 4 reports showing important model metrics.

Udacity provides a **starter** containing:
- template scripts for each step
- fabricated datasets for model training

## The workspace (Udacity)

You’ll complete the project in the Udacity Workspace. It contains all compute resources needed.

There are **eight** key locations in the workspace:

- `/home/workspace` — root directory (default when workspace loads)
- `/practicedata/` — practice datasets
- `/sourcedata/` — source datasets for training
- `/ingesteddata/` — compiled dataset output from ingestion
- `/testdata/` — test datasets
- `/models/` — production model artifacts
- `/practicemodels/` — practice model artifacts
- `/production_deployment/` — final deployed model artifacts

### Notes about the workspace

Files under `/home/workspace/` are saved automatically. After ~30 minutes of idle time (tab closed, inactive, laptop asleep, etc.), the workspace may go to sleep. When you return, your files will be restored to the latest saved state, but you will lose open file tabs and running shell sessions.

## Starter files

The starter contains:
- **10** Python scripts
- **1** configuration file
- **1** requirements file
- **5** datasets

### Python scripts

- `training.py` — train an ML model
- `scoring.py` — score an ML model
- `deployment.py` — deploy a trained model
- `ingestion.py` — ingest new data
- `diagnostics.py` — model/data diagnostics
- `reporting.py` — generate model metric reports
- `app.py` — API endpoints
- `wsgi.py` — API deployment helper
- `apicalls.py` — call API endpoints
- `fullprocess.py` — determine whether a model needs redeployment and run other scripts

### Datasets

Fabricated datasets about hypothetical corporations:

- `dataset1.csv`, `dataset2.csv` — in `/practicedata/`
- `dataset3.csv`, `dataset4.csv` — in `/sourcedata/`
- `testdata.csv` — in `/testdata/`

### Other files

- `requirements.txt` — records current versions of required modules
- `config.json` — configuration used by the ML scripts

