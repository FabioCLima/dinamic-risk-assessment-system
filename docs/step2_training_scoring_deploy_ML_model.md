# Step 2 — Training, Scoring, and Deploying the ML Model

Training and scoring are critical because models are only worth deploying if they are trained and evaluated. Re-training and scoring helps you obtain the best possible accuracy over time.

This step requires three scripts:
- one for training an ML model
- one for generating scoring metrics
- one for deploying the trained model

## Starter files

Use these templates from the starter:

- `training.py` (model training)
- `scoring.py` (model scoring)
- `deployment.py` (model deployment)

You will also need `finaldata.csv` (output of Step 1).

## Dataset: `finaldata.csv`

`finaldata.csv` contains records of corporations and their historical attrition outcomes. Each row is one corporation. Columns:

- `corporation`: 4-character abbreviation (not used for modeling)
- `lastmonth_activity`: numeric feature
- `lastyear_activity`: numeric feature
- `number_of_employees`: numeric feature
- `exited`: target label (1 = exited, 0 = did not exit)

Target:
- `exited` (final column)

Do not use:
- `corporation` (first column)

Use as predictors:
- the three numeric columns

Directories for reading/writing are configured in `config.json`.

## Model training (`training.py`)

Build a training function for an attrition risk model. It must:

1. Read `finaldata.csv` with Pandas from the directory specified in `output_folder_path` (in `config.json`).
2. Train an ML model using scikit-learn.
   - The starter file includes a `LogisticRegression` model that you should use.
3. Save the trained model to:
   - Filename: `trainedmodel.pkl`
   - Directory: `output_model_path` (in `config.json`)

Note:
- This project is about building a monitorable and updatable pipeline, not maximizing accuracy. A reasonable working model is sufficient.

## Model scoring (`scoring.py`)

Implement a scoring function that:

1. Reads test data from `test_data_path` (in `config.json`).
2. Loads the trained model from `output_model_path` (in `config.json`).
3. Calculates the **F1 score** of the model on the test dataset.
4. Writes the F1 score to:
   - Filename: `latestscore.txt`
   - Directory: `output_model_path` (in `config.json`)

The file should contain just a single number, e.g.:

```text
0.6352419
```

## Model deployment (`deployment.py`)

Implement a deployment function that **copies** (does not create new files) into the production deployment directory.

It must copy:

- `trainedmodel.pkl` (trained model)
- `latestscore.txt` (model score)
- `ingestedfiles.txt` (record of ingested data files)

Copy from their original locations into:
- `prod_deployment_path` (in `config.json`)

## Tasks (checklist)

### `training.py`

1. Read `finaldata.csv` using Pandas
2. Train the ML model using the specified algorithm/requirements
3. Save the trained model to `trainedmodel.pkl`

### `scoring.py`

1. Take an ML model and test dataset as inputs
2. Calculate the F1 score on the test dataset
3. Save the F1 score to `latestscore.txt`

### `deployment.py`

1. Copy `trainedmodel.pkl` to `prod_deployment_path`
2. Copy `latestscore.txt` to `prod_deployment_path`
3. Copy `ingestedfiles.txt` to `prod_deployment_path`

## Submission files to download and save locally

1. Completed `training.py`
2. Completed `scoring.py`
3. Trained model `trainedmodel.pkl`
4. Scoring file `latestscore.txt`
5. Completed `deployment.py`

