# Implementation status

## Implemented code

- Collection object ingestion with provenance field and SQLite persistence.
- Physical location observation and discrepancy case generation.
- Review workflow requiring reviewer and separate evidence reference.
- Append-only application event records.
- Non-AI rule-based triage baseline.
- Image feature extraction (8x8 grayscale average hash) and candidate retrieval.
- Trainable logistic risk model with feature contributions and explicit unvalidated status.
- Advisory capacity-constrained preservation ranking.
- Local development JSON API and unit tests.

## Important distinctions

- Average-hash matching is a **computer-vision baseline**, not a learned image recognition model.
- Logistic regression is a **trained ML algorithm**, but the provided test data is synthetic and does not establish accuracy on real collections.
- Model scores are not calibrated probabilities of deterioration.
- Risk-ranking logic is a deterministic planning baseline, not learned optimization.
- Evidence-reference strings are not independent verification of the referenced evidence.
- No institutional deployment, expert review, or performance superiority is claimed.

## Remaining engineering work

1. Integrate model/image assessments with persisted objects and API routes.
2. Add authenticated users, authorization, secure media storage, and tamper-evident audit design.
3. Build image capture and stewardship dashboard interfaces.
4. Acquire permitted labeled datasets and define reproducible train/validation/test partitions.
5. Establish computer-vision model benchmarks beyond average hash.
6. Validate risk models against independent labels and longitudinal outcomes where available.
7. Run cross-schema, robustness, security, load, and expert workflow tests.
8. Conduct authorized institutional pilot evaluation.

All tests are engineering checks until their actual execution and results are independently verified.
