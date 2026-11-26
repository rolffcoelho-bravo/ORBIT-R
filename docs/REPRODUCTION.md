# Reproducible research — first release

The original OPS-SAT-AD v1 raw file is `segments.csv` (not `dataset.csv`, which contains derived features). Official record DOI: 10.5281/zenodo.12588359. Pin and verify upstream MD5 `1f4b6ffd0359efac96a6698ff557e0f9`. The source raw telemetry is **not bundled in the Git repository**. The real dataset remains unmodified on disk; the browser sees only selected measurements.

Install: `python -m pip install -e '.[server,dev]'`. Get real data: `python -m orbitr.cli fetch-data` (may require manual download if Zenodo rate-limits). Audit: `python -m orbitr.cli audit-data`. Replay: `python -m orbitr.cli replay`. Server: `uvicorn orbitr.app:app --port 8080`. Or run Docker Compose after acquiring data.

No evidence of operational benefit or novel mathematical theory has been established. Reference thresholds are empirical and not false-alarm guarantees. OPS-SAT consists of labeled excerpts, not continuous full-mission telemetry: do not compute false alerts per spacecraft-day from these excerpts. Private novel research remains in the separately access-controlled repository, and the public tool never imports it. No project Zenodo DOI exists.
