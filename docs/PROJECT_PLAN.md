# Project Plan — AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform

**Project Title:** AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform  
**Research Working Title:** Real-Time, Stability-Aware Customer Segmentation and Personalized WhatsApp Campaign Recommendation
**Degree:** BE Information Technology  
**Second Review Deadline:** 19–24 October 2026  
**Team Size:** 4 members
**Team Members:** Sarthak Gawari, Yash Kachale, Sushant Bhanwase, Jaykumar Kale

---

## Research Question

> Can a stability-aware decision layer improve the reliability of real-time, RFM-based customer segmentation and personalized campaign recommendations while maintaining low processing latency and enforcing marketing eligibility constraints?

---

## Objectives

1. Build a robust CSV transaction data ingestion pipeline with validation and cleaning.
2. Implement genuine RFM feature engineering at the customer level.
3. Apply K-Means clustering and evaluate with silhouette, Davies–Bouldin, and Calinski–Harabasz scores.
4. Generate interpretable, data-driven segment labels.
5. Implement explainable marketing-fatigue and consent-eligibility rules.
6. Build a campaign recommendation engine with transparent reasoning.
7. Create a usable React dashboard connected to a FastAPI backend.
8. Design a WhatsApp Business API adapter with mock-by-default behaviour.
9. Build an automated test suite covering all core modules.
10. Produce a review-ready IEEE-style research paper draft.
11. Establish a reproducible batch baseline with dataset hashes, preprocessing configuration, seeds, and generated outputs.
12. Evaluate event-driven or micro-batch customer updates without retraining the complete clustering model for every event.
13. Measure whether stability checks reduce unnecessary segment and recommendation switching while preserving eligibility guarantees.

---

## Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | React 18, TypeScript, Vite | Modern, typed, fast dev server |
| UI Styling | Vanilla CSS + custom design system | No heavy framework dependency |
| Backend | Python 3.11, FastAPI | Fast, async, auto-generates OpenAPI docs |
| ORM | SQLAlchemy 2.0 | Works with SQLite (dev) and PostgreSQL (prod) |
| Database | SQLite (dev) / PostgreSQL (prod) | Zero-config for local development |
| Data Processing | pandas, NumPy | Industry standard |
| Machine Learning | scikit-learn | K-Means, preprocessing, metrics |
| Testing | pytest, pytest-cov | Standard Python testing |
| API validation | Pydantic v2 | Auto-validates request/response schemas |
| Environment | python-dotenv | Secrets outside code |
| WhatsApp | Meta WhatsApp Business API (mock by default) | Official API |

---

## Folder Structure

```
Final-Year-Project/
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── tenant.py
│   │   ├── customer.py
│   │   ├── transaction.py
│   │   ├── segment.py
│   │   ├── campaign.py
│   │   └── message_event.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── rfm.py
│   │   ├── segment.py
│   │   └── campaign.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   ├── ingestion.py
│   │   ├── analysis.py
│   │   ├── segments.py
│   │   ├── recommendations.py
│   │   └── campaigns.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ingestion.py
│   │   ├── rfm.py
│   │   ├── clustering.py
│   │   ├── fatigue.py
│   │   └── recommendations.py
│   ├── adapters/
│   │   ├── __init__.py
│   │   └── whatsapp.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_ingestion.py
│   │   ├── test_rfm.py
│   │   ├── test_clustering.py
│   │   ├── test_fatigue.py
│   │   └── test_recommendations.py
│   ├── scripts/
│   │   └── init_db.py
│   ├── data/
│   │   └── example_transactions.csv
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   ├── FileUpload.tsx
│   │   │   ├── MetricCard.tsx
│   │   │   ├── SegmentTable.tsx
│   │   │   └── RecommendationCard.tsx
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Upload.tsx
│   │   │   ├── Analysis.tsx
│   │   │   ├── Segments.tsx
│   │   │   └── Recommendations.tsx
│   │   └── types/
│   │       └── index.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── docs/
│   ├── PROJECT_PLAN.md     (this file)
│   ├── STATUS.md
│   ├── ARCHITECTURE.md
│   └── REVIEW_CHECKLIST.md
└── README.md
```

---

## Phase Timeline (working backward from 19–24 Oct 2026)

| Phase | Description | Priority | Status |
|-------|-------------|----------|--------|
| 0 | Workspace setup, planning, folder structure | A | ✅ Done |
| 1 | Backend skeleton: FastAPI + SQLAlchemy + health endpoint | A | ✅ Done |
| 2 | CSV ingestion service + validation + example dataset | A | ✅ Done |
| 3 | RFM feature engineering + K-Means clustering + evaluation metrics | A | ✅ Done |
| 4 | Fatigue rules + consent eligibility + campaign recommendations | A | ✅ Done |
| 5 | FastAPI endpoints for all services | A | ✅ Done |
| 6 | React frontend: upload → analysis → segments → recommendations | A | ✅ Done |
| 7 | Automated tests (pytest) | A | ✅ Done |
| 8 | Research paper draft (`.md` and IEEEtran `.tex`) | A | ✅ Done |
| 9 | Review presentation and demonstration materials | A | ✅ Done |
| 10 | Database persistence + multi-tenancy models and isolated services | B | ⚠️ Partial; active workflow not wired |
| 11 | WhatsApp adapter (mock + live skeleton) | B | ⚠️ Partial; mock/live adapters exist, no public webhook route |
| 12 | Live WhatsApp sending (requires credentials) | C | 🔒 Blocked |

## Research Extension Roadmap

The following phases are proposed research work and are not represented as completed implementation.

| Phase | Objective | Likely files | Acceptance criteria |
|---|---|---|---|
| R0 | Reproduce and freeze the batch baseline | `backend/scripts/generate_doc_outputs.py`, `docs/PROJECT_OUTPUTS.md` | One command records dataset hash, row counts, preprocessing, seed, library versions, and metrics. |
| R1 | Persist tenant-aware transaction and event state | `backend/database.py`, `backend/session.py`, routers, models, tests | Restart preserves data; API requests cannot read another tenant; duplicate source events are idempotent. |
| R2 | Add incremental or micro-batch profile updates | New event service, `backend/services/rfm.py`, clustering service, tests | A new event updates the affected customer without full historical recomputation; batch remains a comparison condition. |
| R3 | Add stability assessment | New stability service, schemas, tests | Assignment change, centroid drift, ARI, recommendation switching, and deferred-review decisions are recorded with thresholds. |
| R4 | Add webhook and source-event processing | New webhook router, adapter persistence, integration handoff, tests | Signatures are verified; duplicate events remain idempotent across restarts; delivery status updates persist. |
| R5 | Run the comparative evaluation | New replay/benchmark script, `docs/PROJECT_OUTPUTS.md`, paper | Conditions A/B/C report latency, throughput, switching, stability, overhead, and policy violations with no fabricated results. |

### Research hypotheses

- **H1:** Event-driven profile and recommendation updates have lower event-to-decision latency than the batch workflow.
- **H2:** Stability checks reduce unnecessary segment and recommendation changes under controlled transaction perturbations.
- **H3:** Consent, suppression, and frequency-cap guarantees remain satisfied after the real-time extension.

These are hypotheses to test, not current results.

---

## Key Assumptions and Decisions

1. **SQLite for development**: Zero-configuration; swap to PostgreSQL for production via `DATABASE_URL` env var.
2. **Reference date for RFM**: Set to one day after the latest invoice date in the dataset. Documented per run.
3. **Frequency definition**: Count of distinct `invoice_id` values per customer (not transaction line count).
4. **Cancellation handling**: Invoices starting with 'C' are excluded from RFM calculation with a reason recorded.
5. **Cluster labels**: Generated dynamically from cluster statistics (median R, F, M vs dataset median). Not hardcoded.
6. **WhatsApp live mode**: Disabled by default. Requires `WHATSAPP_LIVE_MODE=true` + valid credentials.
7. **Synthetic metadata**: Any consent/engagement data added to the UCI dataset is clearly labelled SYNTHETIC.
8. **Random seed**: Fixed at `42` for all ML experiments for reproducibility.

---

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| No WhatsApp Business account | Mock adapter covers full development; live sending documented as blocked |
| Small dataset causes degenerate clusters | Minimum K guard; graceful fallback with warning |
| Reviewer expects live WhatsApp demo | Demo script uses SIMULATED mode; clearly labelled |
| UCI dataset license | CC BY 4.0 — verified; citation included |

## Evidence Boundaries

- The checked-in empirical output uses the bundled 57-row synthetic verification dataset, not a checked-in UCI file.
- The reproducible recorded output contains 15 customers, selects `K=3`, and reports silhouette `0.4562`.
- The earlier `K=4`, `0.4328`, `0.8712`, and `194.70` figures have no dataset/run provenance in this repository and must not be presented as verified baseline results.
- SQLAlchemy models, tenant helpers, webhook parsing/deduplication, LinUCB, and CRM/POS parsers exist, but the active upload-to-recommendation workflow remains process-local and does not persist through those components.
