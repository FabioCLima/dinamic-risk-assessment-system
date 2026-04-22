# Standout Suggestions (Optional)

## 1) PDF reports

In Step 4 (**Reporting**), you set up a script that generates a confusion matrix plot. Instead of outputting only the raw plot, create a script that generates a **PDF report** that includes:

- The confusion matrix plot from `reporting.py`
- Summary statistics and other diagnostics

This enables faster and more complete reporting that can help your project stand out.

### Implementation notes

- Extend `reporting.py` to generate a PDF.
- You may need to install a PDF library (e.g., `reportlab`).
- Useful content to include in the PDF:
  - Confusion matrix plot
  - Outputs of the API endpoints from `app.py`
  - Model F1 score (stored in `latestscore.txt`)
  - Ingested training files (stored in `ingestedfiles.txt`)

## 2) Time trends

Enable your scripts to store diagnostics from previous iterations of your model and generate reports about **time trends**. Examples:

- How the percent of NA values changes over weeks/months
- Whether ingestion/training timing increases or decreases over time

### Implementation options

- Create a directory like `/olddiagnostics/` and copy diagnostic outputs into it each run.
- Add timestamps to diagnostic output filenames (e.g., `ingestedfiles_<timestamp>.txt`, `latestscore_<timestamp>.txt`).

## 3) Database setup

Instead of storing results in `.txt` and `.csv` files, store datasets and records in **SQL databases** to improve performance and reliability.

### Implementation notes

- Set up SQL databases in the workspace.
- In Python, you can use a module like `mysql-connector-python`.
- Create a script like `dbsetup.py` to initialize databases.
- Example databases/tables:
  - ingested files history
  - model scores history
  - model diagnostics history
- Update `ingestion.py`, `scoring.py`, and `diagnostics.py` to write to these databases each run.

