# ORBIT-R Technical Report 001 — Work in progress
**Institution:** ShockBridge Pulse Research Lab. No performance results established yet.

## Industrial problem
Satellite controllers need early evidence of developing subsystem faults without wasting engineering hours on expected changes, rare operational events, missing measurements, or unexplainable alerts.

## Engineering artifact
Public telemetry pipeline using genuine OPS-SAT-AD v1 measured segments, source SHA-256 and pinned MD5; chronological train/test isolation and calibration, robust baseline, SQLite evidence, historical replay, read-only FastAPI, Docker Compose and GitHub CI.

## Scientific limitation
OPS-SAT comprises manually curated single-channel excerpts; it does not provide full continuous command-aligned fleet telemetry. It cannot validate realistic alerts per spacecraft-day or command-conditioned root-cause detection. The private estimator remains a hypothesis pending primary dataset and theory review.

## Required evidence (NOT YET COLLECTED)
Exact data checksum, dataset counts, event-level holdout performance, rare nominal rejection, latency and resource budgets, confidence intervals, missingness stress, independent replication, safety/security review.

## Requirements before field pilot
Authorized live interface, authenticated dashboard, read-only feed, robust ingestion, retention and access policies, backpressure, sustained service monitoring, domain review, failure and rollback plans. Flight-control commands excluded.

## Scientific disposition
No operational benefit or novel mathematical method is asserted in this report. No ORBIT-R Zenodo DOI exists.
