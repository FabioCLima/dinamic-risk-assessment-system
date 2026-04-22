"""Step 4 — reporting."""


def _bootstrap(patched_modules):
    patched_modules["ingestion"].merge_multiple_dataframe()
    patched_modules["training"].train_model()
    patched_modules["scoring"].score_model()
    patched_modules["deployment"].store_model_into_pickle()


def test_generate_confusion_matrix_plot_writes_png(patched_modules):
    _bootstrap(patched_modules)
    reporting = patched_modules["reporting"]
    project_root = reporting._get_project_dir()

    output = reporting.generate_confusion_matrix_plot()

    assert output.exists()
    assert output.name == "confusionmatrix.png"
    assert output.parent == project_root / "models"
    # PNG magic bytes: 89 50 4E 47
    assert output.read_bytes()[:4] == b"\x89PNG"


def test_generate_confusion_matrix_accepts_custom_filename(patched_modules):
    _bootstrap(patched_modules)
    reporting = patched_modules["reporting"]

    output = reporting.generate_confusion_matrix_plot(output_filename="confusionmatrix2.png")
    assert output.name == "confusionmatrix2.png"
    assert output.exists()
