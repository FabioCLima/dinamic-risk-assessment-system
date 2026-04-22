# Step 3 — Model and Data Diagnostics

Model and data diagnostics are important because they help you find problems (if any exist) in your model and data. Understanding these problems helps you resolve them quickly and ensure the model performs as well as possible.

In this step, you’ll create a script that performs diagnostic tests related to your model as well as your data.

## Starter file

Implement this step in: `diagnostics.py`.

This step also relies on: `config.json` (to locate the directories where files should be read/written).

## Requirements

### 1) Model predictions

Create a function that returns predictions made by your **deployed** model.

- Input: a dataset as a **Pandas DataFrame**
- Model loading: read the deployed model from `prod_deployment_path` (from `config.json`)
- Output: a `list` of predictions with the **same length** as the number of rows in the input dataset

### 2) Summary statistics

Create a function that calculates summary statistics on your data:

- Statistics: **mean**, **median**, and **standard deviation**
- Columns: compute these for **each numeric column** in the dataset
- Dataset location: load the dataset stored in `output_folder_path` (from `config.json`)
- Output: a Python `list` containing all summary statistics for every numeric column

### 3) Missing data

Create a function to check for missing data (NA values).

- For each column:
  - count the number of NA values
  - compute the percent of the column that is NA
- Dataset location: load the dataset stored in `output_folder_path` (from `config.json`)
- Output: a `list` with one element per column, where each element is the **percent NA** for that column

### 4) Timing

Create a function that times how long it takes to perform the important tasks of the project:

- Data ingestion (`ingestion.py` from Step 1)
- Model training (`training.py` from Step 2)

Notes:
- This function takes no arguments.
- Output: a `list` with **two** timing measurements (seconds): `[ingestion_time, training_time]`

### 5) Dependencies

Create a function that checks whether the module dependencies are up-to-date.

- Use the currently installed versions (recorded in `requirements.txt`)
- Use `pip` (via a terminal command) to retrieve the latest available versions
- Output: a table with 3 columns:
  1. module name
  2. installed version
  3. latest available version

Note: you don’t need to reinstall or change dependencies; this is a check only.

## Tasks (checklist)

- [ ] Calculate summary statistics (mean, median, standard deviation) for each numeric column in the dataset
- [ ] Calculate the percent of each column that consists of NA values
- [ ] Measure the timing of important ML tasks (data ingestion and training)
- [ ] Check whether module dependencies are up-to-date
- [ ] Make predictions for an input dataset using the current deployed model

