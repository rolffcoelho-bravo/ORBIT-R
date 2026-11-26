# Multichannel source qualification — G01 work in progress

Source candidate: ESA Anomaly Dataset, **version DOI 10.5281/zenodo.15237121**, record 15237121, concept DOI 10.5281/zenodo.12528695, published 2025-04-17. Its three mission archives are 11,609,189,449 bytes in total. The source metadata and file digests below were checked against the Zenodo API in the earlier local provenance audit; recheck immediately before acquisition.

| File | Bytes | Publisher MD5 |
| --- | ---: | --- |
| ESA-Mission1.zip | 3,776,246,073 | `9770ad12ed730238f37c42d5c27ab436` |
| ESA-Mission2.zip | 4,098,539,932 | `bfc72012691427d9327eb41f726ce45e` |
| ESA-Mission3.zip | 3,734,403,444 | `d63943f09c81378acd9fc5e565ecc66e` |

Official URLs follow `https://zenodo.org/api/records/15237121/files/<filename>/content`. The official ESA dataset repository identifies CC BY 3.0 IGO, while the Zenodo v2 API omitted a license field when checked. This discrepancy needs explicit review before redistribution. Source telemetry stays outside Git.

The published layout has per-mission channel time series in compressed Pickle files, optional telecommand series, `labels.csv`, `anomaly_types.csv`, `channels.csv`, optional `events.csv` and `telecommands.csv`. Annotation rows represent closed time intervals and may repeat an ID over separate segments or channels. Mission 3 is not part of the published benchmark comparison. Exact native column names, mission IDs, command timestamps, and any clock semantics remain **unverified from archive bytes**.

## Acquisition and native schema inspection sequence

1. Recheck record ID, file names, sizes and MD5 via the Zenodo API. Budget at least 8 GB for the two benchmark archives plus extraction and working copies; measure disk and RAM before transfer.
2. Acquire Mission 1 first outside the repository, verify exact byte count and publisher MD5, then calculate local SHA-256. Record UTC acquisition time and the content URL in a local receipt.
3. Inspect archive entry names and sizes without executing Pickle. Extract only named CSV metadata and a bounded channel/command sample into a quarantined working directory. Treat Pickle as untrusted code; do not unpickle until provenance and execution isolation are reviewed.
4. Verify field names, units, time zone, monotonicity, duplicate timestamps, clock resolution, command ID and priority semantics, and sample count. Record source file hash for each extracted sample.
5. Build the native adapter from observed schema. Preserve event time and ingest time separately. Commands become usable context only when their event time and availability time precede the decision time.
6. Repeat on Mission 2 and record any schema or clock differences. Produce an immutable sample receipt and resource measurements before claiming G01 acceptance.

No real multichannel import has occurred yet. This document is a source plan, not evidence of a functioning adapter.

Sources: https://zenodo.org/records/15237121 ; https://github.com/esa/anomaly-dataset/blob/main/LICENSE ; https://data.mlr.press/assets/pdf/v03-23.pdf
