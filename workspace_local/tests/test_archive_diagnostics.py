"""Standout #2 — time-trend archive."""


def test_archive_copies_existing_artifacts_with_timestamp(project_root, monkeypatch):
    import archive_diagnostics
    monkeypatch.setattr(archive_diagnostics, "_get_project_dir", lambda: project_root)

    # Seed a couple of "current" artifacts.
    (project_root / "ingesteddata" / "ingestedfiles.txt").write_text("a.csv\n")
    (project_root / "models" / "latestscore.txt").write_text("0.42\n")

    written = archive_diagnostics.archive_current_diagnostics()

    archive_dir = project_root / "olddiagnostics"
    assert archive_dir.exists()
    assert len(written) == 2
    names = sorted(p.name for p in written)
    # Files keep their stem, gain a timestamp, preserve their extension.
    assert any(n.startswith("ingestedfiles_") and n.endswith(".txt") for n in names)
    assert any(n.startswith("latestscore_") and n.endswith(".txt") for n in names)


def test_archive_skips_missing_sources(project_root, monkeypatch):
    import archive_diagnostics
    monkeypatch.setattr(archive_diagnostics, "_get_project_dir", lambda: project_root)

    # Nothing present at all → must not raise, returns empty list.
    written = archive_diagnostics.archive_current_diagnostics()
    assert written == []
    assert (project_root / "olddiagnostics").exists()
