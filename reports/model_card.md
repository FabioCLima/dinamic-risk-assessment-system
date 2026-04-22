# Model Card: Customer Attrition Risk

## Model details

- **Model type**: Logistic Regression
- **Task**: Binary classification (`exited` vs `not exited`)
- **Primary metric**: F1 score

## Intended use

Support customer success or retention teams by prioritizing accounts with higher churn risk.

## Data summary

- Source: account-level activity features
- Example features:
  - `lastmonth_activity`
  - `lastyear_activity`
  - `number_of_employees`

## Performance snapshot

Fill this section with the latest validated metrics:

- Validation/test F1: `TODO`
- Baseline F1: `TODO`
- Delta vs deployed model: `TODO`

## Limitations

- Simplified feature set with limited temporal context.
- File-based orchestration is practical for small projects but not a full model registry setup.
- No explicit fairness slice analysis yet.

## Operational controls

- Retraining trigger: new source files detected
- Deployment gate: deploy only when candidate F1 is strictly greater than deployed F1
- Monitoring: diagnostics endpoint + generated reports + optional historical archive

## Responsible use notes

Predictions should inform, not replace, human decisions. This system should be used together with domain context (contract terms, support history, and account tier).
