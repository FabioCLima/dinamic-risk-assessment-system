"""Standout #1 — PDF report."""
from types import SimpleNamespace


def _bootstrap(patched_modules):
    patched_modules["ingestion"].merge_multiple_dataframe()
    patched_modules["training"].train_model()
    patched_modules["scoring"].score_model()
    patched_modules["deployment"].store_model_into_pickle()


def test_pdf_report_written_with_expected_sections(patched_modules, monkeypatch):
    _bootstrap(patched_modules)
    reporting = patched_modules["reporting"]
    diagnostics = patched_modules["diagnostics"]
    project_root = reporting._get_project_dir()

    # Stub pip subprocess calls (dependencies table).
    monkeypatch.setattr(
        diagnostics.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=0, stdout="[]", stderr=""),
    )

    pdf_path = reporting.generate_pdf_report()

    assert pdf_path.exists()
    assert pdf_path.parent == project_root / "models"
    # PDF magic header.
    assert pdf_path.read_bytes().startswith(b"%PDF-")
    # Also produced the confusion matrix it embeds.
    assert (project_root / "models" / "confusionmatrix.png").exists()
