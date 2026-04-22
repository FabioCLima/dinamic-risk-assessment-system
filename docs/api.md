# API Overview

The runtime API is served by `workspace_local/app.py` and currently exposes four endpoints:

- `POST /prediction`
  - Input JSON: `{"filepath": "testdata/testdata.csv"}`
  - Output: prediction list (or error object)
- `GET /scoring`
  - Output: latest F1 score
- `GET /summarystats`
  - Output: dataset summary statistics
- `GET /diagnostics`
  - Output: timings, missingness, and outdated dependency report

## Why this matters in portfolio context

This demonstrates that the project does not stop at model training; it also delivers model outputs and diagnostics as a service interface that could be integrated by other systems.

## Example call

```bash
curl -X POST "http://127.0.0.1:8000/prediction" \
  -H "Content-Type: application/json" \
  -d '{"filepath":"testdata/testdata.csv"}'
```
