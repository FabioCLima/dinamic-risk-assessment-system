# Step 1 — Data Ingestion

Data ingestion is important because all ML models require datasets for training. Instead of using a single, static dataset, you’ll create a script that is flexible enough to work with constantly changing sets of input files. This makes ingestion smooth even when data is complex.

In this step, you’ll read data files into Python and write them to an output file that will be the **master dataset**. You’ll also save a record of which files were read.

## Starter files

For this step, you’ll work with:

- `ingestion.py` (template to implement ingestion)
- `config.json` (configuration)
- `practicedata/` datasets: `dataset1.csv` and `dataset2.csv`

## Using `config.json` correctly

`config.json` is used throughout the project and contains these entries:

- `input_folder_path`: where the project looks for input data to ingest and use for training. Changing this changes the data source.
- `output_folder_path`: where to store ingestion outputs. In the starter, it points to `ingesteddata/`.
- `test_data_path`: where the test dataset is located.
- `output_model_path`: where to store trained models and scores.
- `prod_deployment_path`: where to store production models/artifacts.

Initial setup:
- read from `practicedata/`
- write models to `practicemodels/`

When finishing the project, update `config.json` so you:
- read from `sourcedata/`
- write models to `models/`

## Reading data and compiling a dataset

In `ingestion.py`, you must:

1. Automatically detect all `.csv` files in the folder specified by `input_folder_path`.
2. Read each CSV into Python (Pandas).
3. Combine them into a single DataFrame.
4. Remove duplicate rows so the final dataset contains only unique rows.

Important:
- Do **not** hard-code filenames.
- The script must work even if the number of files or their names change.

## Writing the dataset

Save the final merged dataset to:

- Filename: `finaldata.csv`
- Directory: `output_folder_path` (from `config.json`)

In the starter configuration, this means:
- `ingesteddata/finaldata.csv`

## Saving a record of ingestion

Create a record of every CSV filename read during ingestion and store it in:

- Filename: `ingestedfiles.txt`
- Directory: `output_folder_path` (from `config.json`)

The file should contain a list of the filenames of every `.csv` that was read.

