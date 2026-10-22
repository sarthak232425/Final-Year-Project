# Research Paper Draft

**Working title:** Real-Time, Stability-Aware Customer Segmentation and Personalized WhatsApp Campaign Recommendation
**Baseline system:** AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform
**Authors:** Sarthak Gawari, Yash Kachale, Sushant Bhanwase, and Jaykumar Kale
**Affiliation:** Department of Information Technology, Pune Institute of Computer Technology (PICT), Pune, India
**IEEE source:** [RESEARCH_PAPER_DRAFT.tex](RESEARCH_PAPER_DRAFT.tex)
**Status:** Preliminary research draft; proposed extension results are pending.

## Evidence Notice

This draft distinguishes the implemented batch baseline from the proposed real-time research extension. The checked-in repository contains a synthetic 57-row verification dataset with 15 customers. Its generated output records 52 retained rows, 2 cancellations, 5 dropped rows, 1 duplicate, and a selected `K=3` with silhouette `0.4562`. The older `K=4` values (`0.4328`, `0.8712`, `194.70`) do not have dataset/run provenance in this repository and are not used as verified results here.

No event-driven ingestion, incremental clustering, stability-assessment layer, latency benchmark, throughput benchmark, ARI result, or recommendation-switching result is claimed. These are proposed experiments.

## Abstract

This paper proposes an extension to an implemented batch customer segmentation and marketing recommendation platform. The baseline validates retail transactions, computes customer-level Recency, Frequency, and Monetary (RFM) features, selects a K-Means model using internal clustering metrics, generates dynamic segment labels, and applies consent, suppression, recency, and rolling frequency-cap rules before campaign recommendation. The proposed study introduces event-driven or micro-batch profile updates and a stability-assessment layer that can flag material or unstable segment and recommendation changes. The evaluation will compare batch processing, event-driven updates without stability checks, and event-driven updates with stability checks. Planned measures include latency, throughput, segment switching, recommendation switching, cluster stability, processing overhead, and policy violations. The proposed real-time hypotheses remain untested.

## Research Question

Can a stability-aware decision layer improve the reliability of real-time, RFM-based customer segmentation and personalized campaign recommendations while maintaining low processing latency and enforcing marketing eligibility constraints?

## Hypotheses

- **H1:** Event-driven profile and recommendation updates have lower event-to-decision latency than the existing batch workflow.
- **H2:** Stability checks reduce unnecessary segment and recommendation changes under controlled transaction disturbances.
- **H3:** Consent, suppression, and frequency-cap guarantees remain satisfied after the real-time extension.

These are hypotheses, not established findings.

## Implemented Baseline

The existing baseline provides:

1. CSV validation, aliases, duplicate handling, and cancellation isolation.
2. RFM calculation using distinct invoice frequency and transaction monetary totals.
3. `log1p` monetary transformation and `RobustScaler` preprocessing.
4. K-Means evaluation using silhouette, Davies-Bouldin, and Calinski-Harabasz metrics.
5. Dynamic cluster labels based on cluster statistics.
6. Explainable rule-based campaign recommendations.
7. Consent, suppression, recency, and rolling 30-day frequency-cap checks.
8. FastAPI endpoints and a React dashboard for the batch workflow.
9. A mock WhatsApp adapter whose output is labelled `SIMULATED`.

The active upload and analysis flow is process-local and uses `backend/session.py`. SQLAlchemy models, tenant helpers, webhook parsing/deduplication, LinUCB, and CRM/POS parsers exist as isolated components but are not fully wired into the active workflow.

## Verified Baseline Results

| Measure | Recorded value |
|---|---:|
| Raw bundled rows | 57 |
| Customers | 15 |
| Rows retained | 52 |
| Cancellations isolated | 2 |
| Rows dropped | 5 |
| Duplicate lines | 1 |
| RFM reference date | 2024-10-06 |
| Selected K | 3 |
| Silhouette score | 0.4562 |
| Davies-Bouldin index | 0.7150 |
| Calinski-Harabasz score | 13.42 |

These are repository-recorded outputs from the bundled synthetic verification dataset. They are not UCI benchmark results and do not demonstrate real-world marketing effectiveness.

## Proposed Methodology

The planned comparison is:

- **A. Batch baseline:** Recompute the existing workflow after a batch of events.
- **B. Event-driven without stability:** Update affected customer profiles and recommendations without a stability gate.
- **C. Event-driven with stability:** Compare candidate assignments and recommendations with prior state, record drift and switching, and defer or flag unstable decisions.

Historical transaction replay may simulate an event stream, but it must be labelled replay-based simulation. Each run should record the dataset hash, event order, preprocessing settings, random seed, software versions, hardware, batch size, and model parameters.

Candidate incremental strategies include affected-customer recomputation, micro-batches, and `MiniBatchKMeans`. Full retraining for every event should be treated as a comparison condition rather than the default design.

## Planned Metrics

- Event-to-profile-update latency.
- Event-to-recommendation latency.
- Throughput at multiple event loads and micro-batch sizes.
- Segment switching rate.
- Recommendation switching rate.
- Adjusted Rand Index or another partition similarity measure.
- Centroid drift and stability under perturbation.
- Processing overhead from stability assessment.
- Consent, suppression, and frequency-cap violations.

Perturbations should include normal purchases, repeated purchases, isolated high-value transactions, duplicate events, out-of-order events, and transactions near segment boundaries. Ablations should remove the stability layer, fatigue gate, and incremental update path separately.

## Research Gap and Contribution Scope

The contribution is framed as an applied empirical evaluation, not a first-ever claim. Existing work covers RFM segmentation, clustering validation, data-stream mining, and customer interaction fatigue separately. This project evaluates their combination in an auditable campaign-decision workflow where policy constraints remain mandatory. The precise novelty and generalisability must be assessed after the experiments are executed.

## Limitations

The bundled dataset is small and synthetic. Consent and engagement fields are designed test metadata. No UCI Online Retail file is checked into the repository. Replay experiments will not reproduce live network or source-system behaviour. Internal clustering scores do not establish campaign effectiveness. Stability thresholds are policy and engineering choices requiring sensitivity analysis.

## References

The IEEEtran source contains the formatted bibliography, including Hughes (1994), MacQueen (1967), Rousseeuw (1987), Davies and Bouldin (1979), Calinski and Harabasz (1974), Chen et al. (2012), Fader et al. (2005), Godfrey et al. (2011), Kumar and Reinartz (2016), Verhoef et al. (2015), Bifet and Kirkby (2009), Aggarwal et al. (2003), and Hubert and Arabie (1985).

This Markdown file is a working companion. It is not a final IEEE submission; use [RESEARCH_PAPER_DRAFT.tex](RESEARCH_PAPER_DRAFT.tex) for IEEEtran compilation.
