# ADR 0006 — Retain model evidence without executable estimator artifacts

Status: accepted — 2026-09-15

## Decision

Phase 6 trains bounded models synchronously from tenant-owned cleaned datasets and
persists typed JSON reports: split metadata, metrics, confusion matrices, version,
and permutation effects. It does not store pickle, joblib, or another executable
model serialization. The API owns target and feature definitions; callers choose a
dataset and experiment name but cannot submit code or estimator parameters.
Target thresholds and categorical vocabulary are learned from training rows after
the split, so holdout observations cannot influence fitted state.

## Why

This first vertical needs reviewable experiment tracking and a safe local workflow.
Python model serialization can execute code during loading, while a 5,000-row
interactive bound keeps deterministic comparison within the existing API budget.
Artifact signing, object storage, asynchronous training, and deployment belong to
later progression levels with their own trust boundaries.

## Consequences

Experiments can be inspected and compared after restart, but cannot yet be served
for inference. Reproducing one run retrains from the retained cleaned dataset using
the recorded seed and dependency version. A later model registry must use a signed,
scanned artifact format and a separate serving identity.
