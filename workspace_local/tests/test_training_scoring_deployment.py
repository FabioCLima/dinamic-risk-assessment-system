"""Step 2 — training, scoring, deployment."""
import pickle

from sklearn.linear_model import LogisticRegression


def _ingest(patched_modules):
    patched_modules["ingestion"].merge_multiple_dataframe()


def test_train_model_persists_logistic_regression(patched_modules):
    _ingest(patched_modules)
    training = patched_modules["training"]
    project_root = training._get_project_dir()

    model = training.train_model()

    model_path = project_root / "models" / "trainedmodel.pkl"
    assert model_path.exists()
    assert isinstance(model, LogisticRegression)

    with model_path.open("rb") as f:
        loaded = pickle.load(f)
    assert isinstance(loaded, LogisticRegression)
    assert list(loaded.classes_) == [0, 1]


def test_train_model_raises_when_finaldata_missing(patched_modules):
    # Intentionally skip ingestion.
    training = patched_modules["training"]
    try:
        training.train_model()
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError when finaldata.csv is absent")


def test_score_model_writes_single_float(patched_modules):
    _ingest(patched_modules)
    patched_modules["training"].train_model()

    scoring = patched_modules["scoring"]
    project_root = scoring._get_project_dir()

    score = scoring.score_model()

    score_path = project_root / "models" / "latestscore.txt"
    assert score_path.exists()
    content = score_path.read_text().strip()
    # The spec demands a single number; parsing must succeed.
    assert float(content) == score
    assert 0.0 <= score <= 1.0


def test_score_model_requires_trained_model(patched_modules):
    _ingest(patched_modules)
    scoring = patched_modules["scoring"]
    try:
        scoring.score_model()
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError when trainedmodel.pkl is missing")


def test_deploy_copies_three_artifacts(patched_modules):
    _ingest(patched_modules)
    patched_modules["training"].train_model()
    patched_modules["scoring"].score_model()

    deployment = patched_modules["deployment"]
    project_root = deployment._get_project_dir()
    deployment.store_model_into_pickle()

    prod_dir = project_root / "production_deployment"
    for expected in ("trainedmodel.pkl", "latestscore.txt", "ingestedfiles.txt"):
        assert (prod_dir / expected).exists(), f"missing {expected} in production_deployment"


def test_deploy_raises_when_source_artifact_missing(patched_modules):
    _ingest(patched_modules)
    # Train but skip scoring — latestscore.txt won't exist.
    patched_modules["training"].train_model()

    try:
        patched_modules["deployment"].store_model_into_pickle()
    except FileNotFoundError:
        return
    raise AssertionError("expected FileNotFoundError when latestscore.txt is missing")
