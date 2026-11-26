# ORBIT-R — Predictive Satellite Health & Mission Assurance

Independent research by ShockBridge Pulse Research Lab. **Public evidence and operational-monitoring reference code only.** Genuine OPS-SAT source: [Zenodo v1](https://doi.org/10.5281/zenodo.12588359). Never represent historical replay as a live spacecraft feed.

**Project objective:** detect emerging spacecraft health deviations early while reducing false-alarm burden and reporting when evidence is insufficient. Public implementation provides source provenance, time-ordered historical replay, an explicitly non-novel baseline, monitoring dashboard and tests. Experimental original mathematics is held separately in the *private* ORBIT-R-CORE repository.

**Start:** `pip install -e '.[server,dev]'`; `python -m orbitr.cli fetch-data`; `python -m orbitr.cli audit-data`; `uvicorn orbitr.app:app --port 8080`. Or `docker compose up --build -d` after the raw file is verified and placed in `data/raw/segments.csv`.

**Status:** research scaffold, not flight-qualified, no validated novel method and no project Zenodo DOI. Never push raw datasets or private code. All empirical claims require raw-data hashes and held-out real-data evaluation. See local v0.1 development bundle for full reproducibility templates.
