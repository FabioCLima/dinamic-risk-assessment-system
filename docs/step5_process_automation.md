# Step 5 — Process Automation

Process automation is important because it eliminates the need to manually perform the individual steps of the ML model scoring, monitoring, and re-deployment process.

In this step, you’ll create scripts that automate ML model scoring and monitoring. This includes checking the criteria that require model re-deployment, and re-deploying models as necessary.

## The model re-deployment process

```
Check for new data ──► New data: Ingest + Check drift ──► Model drift: Deploy best model + Diagnostics
        │                            │
        ▼                            ▼
  No new data:               No model drift:
  Process ends               Process ends
```

## Tasks — `fullprocess.py`

- [ ] Check for new data and read the files, if any exist
- [ ] Check for model drift
- [ ] Re-deploy if there is **new data** AND **model drift**
- [ ] Run `apicalls.py` and `reporting.py` using the most recently deployed model

## Cron job

- [ ] Configure a cron job that runs `fullprocess.py` automatically every **10 minutes**

## Final deliverables (save locally)

- [ ] Script: `fullprocess.py`
- [ ] File: `cronjob.txt` containing the one-line cron job
- [ ] Deployed model confusion matrix: `confusionmatrix2.png`
- [ ] API output file: `apireturns2.txt`

## Implementation details

### Update `config.json`

- `input_folder_path`: `/practicedata/` → `/sourcedata/`
- `output_model_path`: `/practicemodels/` → `/models/`

### New data check

1. Read `ingestedfiles.txt` from `prod_deployment_path`
2. Compare it to the CSV files in `input_folder_path`
3. If there are new files, run `ingestion.py`

### Model drift check

1. Read the current score from `latestscore.txt`
2. Generate predictions with the deployed `trainedmodel.pkl` on the most recent data
3. Compute the new score via `scoring.py`
4. Compare scores: if `new_score < current_score` → drift detected

### Re-training and re-deploy

If drift is detected:
- Run `training.py` using the most recent ingested data
- Run `deployment.py` to deploy the new model

### Cron job example (every 10 minutes)

```bash
*/10 * * * * /usr/bin/python3 /home/user/fullprocess.py
```

