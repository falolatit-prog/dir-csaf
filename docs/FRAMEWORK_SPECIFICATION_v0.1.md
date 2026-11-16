# DIR-CSAF Framework Technical and Research Specification

**Version:** 0.1 (initial architecture baseline)  
**Status:** Proposed design; not implemented or validated  
**Repository:** falolatit-prog/dir-csaf

## 1. Controlling proposed endeavor

> To develop and deploy a scalable, data-driven, risk-informed collections stewardship framework that strengthens inventory accountability, improves preservation planning, and safeguards nationally significant cultural heritage collections across U.S. museums and archives.

**Scope rule:** Every feature, experiment, and claimed outcome must trace to inventory accountability, preservation planning, or safeguarding cultural heritage. No deployed system, institutional adoption, prediction accuracy, or preservation improvement is claimed by this specification.

## 2. Architecture baseline

This document follows the previously agreed AI-powered architecture, in order:

1. **Data Acquisition and Integration**: artifact photographs, inventory records, historical documentation, environmental sensors.
2. **Computer Vision** (parallel intelligence pathway): object matching, visual condition analysis, image-based anomalies.
3. **Predictive AI** (parallel intelligence pathway): risk scoring, deterioration forecasting, resource prioritization.
4. **Explainable Decision-Support Engine**: risk evidence, confidence scores, curator and conservator review, audit trails.
5. **Outputs**: inventory verification reports, preservation risk-based action plans, accountability stewardship dashboards.

Computer Vision and Predictive AI are core research components, not optional add-ons. They produce *assessments* for evidence-aware decisions; they do not autonomously certify artifact identity, physical location, or preservation outcomes.

## 3. Layer specifications

### L1. Data Acquisition and Integration

**Inputs:** catalog and accession records; object identifiers and location/movement histories; object images and image metadata; condition assessments; historical documents; environmental observations when available.

**Functions:** schema mapping; source provenance; controlled vocabulary normalization; record linkage with uncertainty; temporal versioning; quality and missingness checks; access control.

**Outputs:** provenance-linked collection object records, observation records, and data quality reports.

**Acceptance evidence:** documented schema and mapping tests; traceable original-source references; rejected/ambiguous record handling; repeatable import of at least two distinct synthetic institutional schemas.

### L2A. Computer Vision

**Research tasks:**
- Candidate image-to-object matching and duplicate-image detection.
- Condition-change assistance using appropriately comparable image pairs.
- Image anomaly detection with explicit distinction between imaging artifacts and object-condition anomalies.

**Inputs:** versioned images, capture context, reference imagery, object metadata where authorized.

**Outputs:** ranked candidates, calibrated or explicitly uncalibrated confidence indicators, image-quality flags, and evidence references.

**Safeguards:** image similarity is not proof of identity, custody, authenticity, or location. Confirmation requires independent physical/documentary corroboration and authorized human review. No automatic inventory case closure from an AI match.

**Evaluation:** top-k retrieval accuracy, precision/recall for specified matching tasks, false-positive rate, subgroup/dataset stratification, calibration, abstention, and image-shift robustness. Condition-change claims require labeled longitudinal images and expert adjudication.

### L2B. Predictive AI

**Research tasks:**
- Risk scoring based on observed conditions, environmental exposures, documentation gaps, and institutional risk factors.
- Deterioration forecasting *only when longitudinal observations and valid outcome labels support it*.
- Resource prioritization under documented budget, urgency, and conservation constraints.

**Outputs:** risk estimates or ordinal categories, evidence and uncertainty, forecast horizons where supportable, and proposed priority rankings.

**Safeguards:** distinguish measured facts from model estimates; flag missingness and out-of-distribution inputs; no unsupported deterioration forecasts. Resource recommendations are advisory and must disclose assumptions and constraints.

**Evaluation:** ranking quality against blinded expert assessments or justified ground truth; discrimination and calibration where applicable; forecasting error against held-out time periods when data permits; prioritization regret and sensitivity to constraints.

### L3. Explainable Decision-Support Engine

**Functions:** combine CV findings, risk model assessments, and source records; produce traceable reasons, alternatives, uncertainties, and required corroboration; route cases for curator/conservator review; maintain immutable-style append-only audit events and role-based approvals.

**Decision states:** proposed, needs-evidence, under-review, approved, rejected, action-in-progress, verified, closed. Any closed case must reference human authorization and supporting evidence.

**Outputs:** evidence packets, investigation recommendations, review decisions, action assignments, and audit histories.

**Evaluation:** evidence completeness, explanation fidelity to actual model inputs/decisions, expert usability, override frequency, inappropriate-closure rate, and audit reconstruction.

### L4. Institutional outputs

**Inventory:** verification reports that distinguish confirmed, discrepant, uncertain, and not-assessed items; reconciliation status and evidence trail.

**Preservation:** risk-based action plans with rationale, urgency, dependencies, responsible roles, resource assumptions, and follow-up verification.

**Accountability:** stewardship dashboards showing coverage, unresolved discrepancies, high-priority risks, overdue actions, and review provenance.

**Safeguard:** dashboards must not treat unresolved cases as confirmed losses or AI suggestions as completed preservation actions.

## 4. Core conceptual data entities

- **CollectionObject:** stable institutional identifier, descriptive metadata, significance/context fields, source links.
- **SourceRecord:** original system/document, ingest timestamp, provenance, version.
- **ImageObservation:** image reference, capture time/context, permissions, quality indicators.
- **PhysicalVerification:** independently observed identifiers, location/custody evidence, verifier, timestamp.
- **ConditionObservation:** assessment, assessor/method, observed date, evidence.
- **EnvironmentalObservation:** metric, value, unit, location, timestamp, sensor quality.
- **ModelAssessment:** model/version, input provenance, task, output, uncertainty, limitations.
- **RiskAssessment:** factors, method/model version, rating, rationale, review status.
- **InvestigationCase:** discrepancy type, status, assigned role, evidence, closure justification.
- **PreservationAction:** proposed intervention, priority, approval, implementation and verification.
- **AuditEvent:** actor, action, time, object/case reference, before/after references.

Identifiers and provenance must remain stable across imports; access to culturally sensitive and restricted collection information must be controlled.

## 5. Research hypotheses and baseline comparisons

These are **testable hypotheses, not findings**:

- **H1, inventory accountability:** AI-assisted verification plus human corroboration improves discrepancy identification and/or resolution efficiency without an unacceptable increase in false confirmations.
- **H2, preservation planning:** risk-informed AI assistance improves agreement with defensible expert priorities or resource-allocation quality relative to defined baselines.
- **H3, accountability:** explainable, audited review improves evidence completeness and decision traceability.
- **H4, robustness/scalability:** performance remains within predefined quality and latency limits across distinct institutional schemas and increasing collection sizes.

**Proposed comparative arms:**
A. Existing/manual or routine workflow baseline.  
B. Conventional non-AI risk-based workflow.  
C. DIR-CSAF with integrated AI and mandatory human verification.  
Optional D. DIR-CSAF without AI, to isolate the incremental contribution of the AI pathways.

Use matched cases, frozen datasets, documented splits, predeclared thresholds, confidence intervals, and failure analysis. Avoid claiming superiority from synthetic-only evaluation. Prevent data leakage across object identities, image sessions, institutions, and time where relevant.

## 6. Evaluation metrics and evidence requirements

| Outcome | Candidate metrics | Evidence required |
|---|---|---|
| Inventory accountability | discrepancy precision/recall; false-confirmation rate; resolution time; verified closure rate | labeled cases, independent verification, workflow timestamps |
| Computer vision | top-k accuracy; precision/recall; calibration; abstention; image-shift sensitivity | labeled images, capture metadata, held-out test sets |
| Preservation planning | risk-ranking agreement; ranking quality; action appropriateness; planning time | blinded expert review, explicit risk rubric, constrained scenarios |
| Forecasting (conditional) | forecast error; calibration; horizon-specific performance | sufficient longitudinal labels and time-based holdouts |
| Stewardship accountability | evidence completeness; audit reconstruction; reviewer overrides | audit events, review decisions, case evidence |
| Scalability | throughput; latency; data import success; error rates | repeatable load tests and multiple institutional schemas |

Define minimum acceptable performance and safety thresholds **before** final testing. Publish negative and inconclusive results as well as successes.

## 7. Validation stages

1. **Specification review:** domain experts assess terminology, assumptions, preservation-risk factors, and decision rules.
2. **Synthetic demonstrator:** generate clearly labeled synthetic records, images only if provenance permits, and controlled discrepancies; establish engineering functionality, not real-world effectiveness.
3. **Retrospective evaluation:** test on appropriately permissioned, de-identified or public institutional datasets with credible labels.
4. **Expert adjudication:** curators, registrars, collections managers, and conservators assess ambiguous findings and preservation recommendations.
5. **Institutional pilot:** only with written partner authorization, documented data governance, and agreed success criteria; start in advisory mode.
6. **Independent validation:** external reviewers reproduce evaluation protocols and assess limitations.

**No pilot partnership or institutional deployment is asserted.**

## 8. Governance, safety, and boundaries

- Preserve provenance, auditability, institutional authority, and collection-specific access restrictions.
- Do not infer legal title, provenance authenticity, repatriation eligibility, or cultural significance solely from an AI model.
- Do not automatically change official inventory records or execute conservation interventions based on model outputs.
- Protect sensitive location and security information; use least-privilege roles and documented retention rules.
- Report model failure modes, dataset bias, missingness, and confidence limitations.
- Preserve human authority for final verification, risk acceptance, and preservation actions.

## 9. Proposed technical implementation (not yet selected or built)

Potential components, subject to design review:
- Python API and AI/CV services.
- Relational database for collection, provenance, workflow, and audit entities.
- Web stewardship dashboard.
- Mobile capture and physical verification client.
- Versioned model and evaluation pipeline.

Technology choices must follow reproducibility, institutional interoperability, maintainability, and data-governance requirements. A particular stack is not part of the endeavor statement.

## 10. Milestones and exit gates

**M0 — Baseline specification:** architecture, traceability, definitions, hypotheses, controls, and metrics documented.  
**M1 — Data foundation:** provenance-preserving ingest and schema validation demonstrated.  
**M2 — AI evidence prototypes:** CV and risk models evaluated separately on frozen datasets with uncertainty reporting.  
**M3 — Integrated decisions:** evidence packets, reviewer approval, case workflow, and audit reconstruction demonstrated.  
**M4 — Controlled comparisons:** predeclared baseline experiments, statistical uncertainty, and failure reports published.  
**M5 — Expert review:** documented external feedback and corrective actions.  
**M6 — Pilot readiness:** governance, performance, access controls, and institutional review completed before any pilot.  
**M7 — Deployment/validation:** only claim after actual authorized institutional use and measured results.

A milestone is complete only when its artifacts and acceptance evidence are linked in the repository.

## 11. Requirements traceability

| Requirement | Architecture | Planned verification |
|---|---|---|
| Scalable | L1, L3, L4 | cross-schema and load tests |
| Data-driven | L1, L2A, L2B | provenance and data-quality tests |
| Risk-informed | L2B, L3 | risk-ranking and action-review evaluation |
| Inventory accountability | L2A, L3, L4 | independent confirmation and discrepancy studies |
| Preservation planning | L2B, L3, L4 | expert evaluation and constrained action planning |
| Heritage safeguarding | L3, L4 | evidence-supported risk mitigation and follow-up |
| U.S. museums and archives | all layers | institution-specific interoperability and authorized pilots |

## 12. Open research decisions

1. Define eligible collection types and institutional contexts without overgeneralizing.
2. Identify legally and ethically usable image/collection datasets and labeling protocols.
3. Agree on an expert-reviewed preservation risk taxonomy and significance criteria.
4. Set objective thresholds for unsafe false confirmations and abstention.
5. Determine whether deterioration forecasting is empirically feasible with available data.
6. Define pilot recruitment, governance, and independent review procedures.
7. Freeze comparison protocols before final model selection or tuning.

---

**Evidence statement:** This file is a proposed technical and research specification. It contains no experimental results, no verified institutional outcomes, and no claim that DIR-CSAF has been deployed.
