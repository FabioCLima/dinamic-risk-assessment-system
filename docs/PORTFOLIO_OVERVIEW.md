# Portfolio Overview: Dynamic Risk Assessment System

## Audience-friendly summary

This project is a practical example of how machine learning is used beyond notebooks.

Instead of stopping at "train a model," it shows how to operate a model over time:
- data ingestion
- quality checks
- evaluation and redeployment criteria
- diagnostics
- API exposure
- process automation

For non-technical readers: think of this as a "health monitoring and auto-update system" for a predictive model.

For technical readers: this is a file-based batch MLOps architecture with model performance gating and automated orchestration.

## Problem statement

Given account-level activity data, estimate the probability that a customer will churn (`exited`) and keep the model updated as new data arrives.

## Business value

- Earlier identification of customer risk
- Faster model maintenance cycle
- Reduced manual effort in retraining decisions
- Better traceability of model and data changes

## What recruiters should notice

1. End-to-end thinking: data -> model -> deploy -> monitor -> automate
2. Operational maturity: idempotent scripts, diagnostics, and testing
3. Practical API layer: model outputs and health information exposed by service endpoints
4. Drift-aware behavior: deploy only when candidate model improves target metric

## Recommended talking points in interviews

- Why F1 score was chosen for classification performance
- Why deployment uses a strict "better-than-current" gate
- Trade-offs of file-based artifacts vs model registry
- How this foundation can evolve to cloud-native orchestration and monitoring
