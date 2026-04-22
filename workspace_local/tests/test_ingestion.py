"""Step 1 — data ingestion."""
import pandas as pd


def test_merge_multiple_dataframe_writes_both_artifacts(patched_modules):
    ingestion = patched_modules["ingestion"]
    project_root = ingestion._get_project_dir()

    merged, filenames = ingestion.merge_multiple_dataframe()

    finaldata = project_root / "ingesteddata" / "finaldata.csv"
    ingested_list = project_root / "ingesteddata" / "ingestedfiles.txt"

    assert finaldata.exists()
    assert ingested_list.exists()
    assert set(filenames) == {"dataset_a.csv", "dataset_b.csv"}
    assert ingested_list.read_text().splitlines() == sorted(filenames)
    assert len(merged) == 8


def test_merge_removes_duplicate_rows(patched_modules):
    ingestion = patched_modules["ingestion"]
    project_root = ingestion._get_project_dir()

    src_a = project_root / "sourcedata" / "dataset_a.csv"
    dup_path = project_root / "sourcedata" / "dataset_c.csv"
    pd.read_csv(src_a).to_csv(dup_path, index=False)

    merged, _ = ingestion.merge_multiple_dataframe()

    # dataset_c is a byte-for-byte copy of dataset_a, so dedup must collapse them.
    assert len(merged) == 8


def test_merge_autodetects_arbitrary_filenames(patched_modules):
    ingestion = patched_modules["ingestion"]
    project_root = ingestion._get_project_dir()

    # Rename to prove nothing is hard-coded.
    (project_root / "sourcedata" / "dataset_a.csv").rename(project_root / "sourcedata" / "weird_name.csv")
    (project_root / "sourcedata" / "dataset_b.csv").rename(project_root / "sourcedata" / "another_one.csv")
    # Non-CSV files must be ignored.
    (project_root / "sourcedata" / "README.txt").write_text("ignore me")

    _, filenames = ingestion.merge_multiple_dataframe()

    assert set(filenames) == {"weird_name.csv", "another_one.csv"}


def test_merge_raises_when_input_folder_empty(patched_modules):
    ingestion = patched_modules["ingestion"]
    project_root = ingestion._get_project_dir()

    for csv_file in (project_root / "sourcedata").glob("*.csv"):
        csv_file.unlink()

    try:
        ingestion.merge_multiple_dataframe()
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("expected FileNotFoundError when no CSVs are present")
