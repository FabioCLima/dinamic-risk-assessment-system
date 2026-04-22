# GitHub First Commit Sequence

Use this sequence when creating your public repository so the history is clean and reviewer-friendly.

## Commit 1: Portfolio framing

**Message**
`docs: add portfolio narrative for technical and non-technical audiences`

**Include**
- `README.md`
- `docs/PORTFOLIO_OVERVIEW.md`
- `docs/architecture.md`
- `docs/api.md`

## Commit 2: Root project scaffolding

**Message**
`build: add root package scaffold and CLI entrypoint`

**Include**
- `pyproject.toml`
- `src/portfolio_pipeline/*`
- `Makefile`
- `configs/*`
- `.gitignore`

## Commit 3: Native pipeline migration

**Message**
`feat: migrate dynamic risk pipeline to src package modules`

**Include**
- `src/dynamic_risk_assessment/*`
- root `config.json`

## Commit 4: Legacy compatibility wrappers

**Message**
`refactor: convert workspace_local scripts into legacy wrappers`

**Include**
- `workspace_local/*.py` wrappers forwarding to `src` modules

## Commit 5: Testing and CI

**Message**
`test: add root tests and GitHub Actions CI workflow`

**Include**
- `tests/*`
- `pytest.ini`
- `.github/workflows/ci.yml`

## Commit 6: Reporting assets templates

**Message**
`docs: add model card and monitoring report templates`

**Include**
- `reports/model_card.md`
- `reports/monitoring_report.md`
- `notebooks/README.md`

## Optional Commit 7: Course artifacts archival

**Message**
`chore: move udacity-specific artifacts to archive folder`

**Include (optional)**
- `starter-file/`, `submission/`, and legacy docs moved to an `archive/` area
- only if you decide to reduce portfolio noise
