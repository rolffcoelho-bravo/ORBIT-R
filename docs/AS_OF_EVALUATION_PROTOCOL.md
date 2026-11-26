# G01 as-of evaluation protocol — pre-registered design

Status: design frozen before any ESA mission model optimization. This defines how partitions will be selected from verified native source time. It does not assert that the current OPS-SAT benchmark split is causal.

1. For each eligible mission, sort observations by normalized UTC event time, preserving stable source order for duplicate timestamps. Audit clock and missingness before splitting. Source ingestion time is never substituted for event time.
2. Determine boundaries at the first observed UTC timestamp at or after the 60th, 75th and 85th percentile of unique event times, calculated **without labels**. The intervals are train, development, calibration and untouched test, respectively. Store exact boundary timestamps and source hashes in a committed protocol addendum before any fit. If mission duration or event counts make these fractions unsuitable, register the alternative before reading test labels.
3. At each boundary, purge any model window crossing the boundary; embargo one maximum feature window plus the declared warning horizon. Define these durations before scoring. Do not use future channel values or telecommands whose availability time exceeds the assessment time.
4. Training may use only train observations. Development chooses architecture and thresholds. Calibration fixes the alert policy once. Test is opened once for final scoring; no iterative retuning on test labels. The previous OPS-SAT 529-segment test result is frozen and excluded from model selection.
5. Report event-wise recall and detection delay only where label onset and observation coverage support them. Count alert episodes and abstentions, with denominators and time-at-risk. Missing/invalid intervals are excluded or modeled explicitly; they are not silently treated as healthy negatives.
6. Keep expert annotations out of the dashboard and inference path. Allow them only in the scoring stage after predictions and timestamps are sealed. Preserve rare nominal, anomaly, gap and invalid categories separately.
7. Publish run metadata: source DOI and local SHA-256, exact split boundaries, command availability policy, software commit, environment, CPU/RAM, warnings, failures and null results.

The first benchmark will be descriptive until native archive clocks, labels and command semantics have been audited. No operational false-alert rate is inferable from curated OPS-SAT excerpts.
