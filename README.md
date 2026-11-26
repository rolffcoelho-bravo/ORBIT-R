# ORBIT-R — Spacecraft Telemetry Research Reference

Public reference code for historical spacecraft telemetry replay. Genuine OPS-SAT source: [Zenodo v1](https://doi.org/10.5281/zenodo.12588359). Never represent historical replay as a live spacecraft feed.

The public implementation provides source provenance, time-ordered historical replay, a reference baseline, monitoring dashboard and tests.

**Start:** `pip install -e '.[server,dev]'`; `python -m orbitr.cli fetch-data`; `python -m orbitr.cli audit-data`; `uvicorn orbitr.app:app --port 8080`. Or `docker compose up --build -d` after the raw file is verified and placed in `data/raw/segments.csv`.

**Status:** research scaffold, not flight-qualified, no validated novel method and no project Zenodo DOI. Never push raw datasets or private code. All empirical claims require raw-data hashes and held-out real-data evaluation.
