# Project Status — AI Customer Segmentation & WhatsApp Marketing Platform

**Last Updated:** 2026-10-22
**Review Deadline:** 19–24 October 2026  
**Current Milestone:** Review 2 MVP complete; real-time stability research extension planned

---

## Current Overall Status: ✅ REVIEW 2 MVP COMPLETE; RESEARCH EXTENSION NOT YET IMPLEMENTED

The batch MVP is runnable and review-ready. The proposed real-time, stability-aware research direction is documented as future work and must not be described as implemented.

### Verified baseline

- CSV ingestion, RFM calculation, K-Means evaluation, dynamic labelling, fatigue rules, recommendations, dashboard views, and mock WhatsApp adapter are implemented.
- The checked-in empirical output uses `backend/data/example_transactions.csv`: 57 raw rows, 15 customers, 52 retained rows, 2 cancellations, 5 dropped rows, and 1 duplicate.
- The recorded baseline selects `K=3` with silhouette `0.4562`, Davies–Bouldin `0.7150`, and Calinski–Harabasz `13.42`.
- The backend workflow is currently process-local and uses the in-memory session; SQLAlchemy models and tenant helpers are not wired into the upload and analysis routers.

### Proposed or incomplete

- Event-driven ingestion, incremental clustering, stability checks, latency/throughput evaluation, persistent webhook handling, and real-time dashboard updates are not implemented.
- The LinUCB service, CRM/POS parsers, webhook signature parsing, and adapter-level deduplication exist as isolated components, not as an integrated research pipeline.
- Live WhatsApp sending remains disabled without verified Meta credentials; no production cloud deployment exists.

### Evidence correction

Earlier documents cited `K=4` metrics (`0.4328`, `0.8712`, `194.70`) and a `9 approved / 6 blocked` audience split. Those values are not supported by the checked-in generated output and are retained only as historical claims requiring provenance. The IEEE draft uses the verified repository-recorded baseline instead.

---

## Milestone Log

### ✅ MILESTONE 0 — Workspace Setup (2026-10-19)
- [x] Workspace inspected and verified
- [x] README.md created
- [x] docs/PROJECT_PLAN.md created
- [x] docs/ARCHITECTURE.md created
- [x] docs/REVIEW_CHECKLIST.md created
- [x] docs/STATUS.md created

### ✅ MILESTONE 1 — Backend Architecture & Models
- [x] FastAPI app with CORS and versioned routers (`backend/main.py`)
- [x] SQLite database connection & session lifecycle (`backend/database.py`, `backend/session.py`)
- [x] Health endpoint GET /health returning service status & timestamp
- [x] Configuration via environment variables (`backend/config.py`, `backend/.env.example`)
- [x] SQLAlchemy ORM models (`backend/models/transaction.py`, `backend/models/customer.py`, `backend/models/campaign.py`)

### ✅ MILESTONE 2 — Data Ingestion & Quality Gate
- [x] CSV upload endpoint `POST /api/v1/ingest/upload`
- [x] Strict validation service (`backend/services/ingestion.py`)
- [x] Cancellation invoice detection (prefix 'C')
- [x] Detailed cleaning summary returned with every upload
- [x] Example dataset bundled (`backend/data/example_transactions.csv`)

### ✅ MILESTONE 3 — RFM Analytics & Unsupervised Clustering
- [x] RFM feature engineering service (`backend/services/rfm.py`)
- [x] K-Means clustering service with automated parameter sweep (`backend/services/clustering.py`)
- [x] Silhouette Score computed (0.4562 at K=3 on the bundled baseline)
- [x] Davies–Bouldin Index computed (0.7150 at K=3 on the bundled baseline)
- [x] Calinski–Harabasz Index computed (13.42 at K=3 on the bundled baseline)
- [x] Dynamic segment labeling based on cluster centroids
- [x] Fully reproducible with `random_seed=42`

### ✅ MILESTONE 4 — Fatigue Prevention & Recommendation Engine
- [x] Strict consent check (`consent_given == True`)
- [x] Suppression list verification (`suppressed == False`)
- [x] Rolling 30-day frequency cap rule (max 3 messages)
- [x] Lifecycle purchase recency window rule
- [x] Rule-based campaign recommendation engine (`backend/services/recommendations.py`)
- [x] Every recommendation paired with natural-language explanation and supporting metrics

### ✅ MILESTONE 5 — REST API Endpoints
- [x] `GET /health` — Service health
- [x] `POST /api/v1/ingest/upload` — Transaction ingestion & cleaning
- [x] `GET /api/v1/ingest/status` — Current ingestion status
- [x] `POST /api/v1/analysis/run` — Executes RFM + clustering
- [x] `GET /api/v1/analysis/rfm` — Paginated customer RFM table
- [x] `GET /api/v1/analysis/metrics` — K-Means evaluation indices
- [x] `GET /api/v1/segments` — Cohort profiles & centroids
- [x] `GET /api/v1/recommendations` — Filterable recommendations with audit checks
- [x] `POST /api/v1/campaigns/preview` — WhatsApp preview with simulation safeguards

### ✅ MILESTONE 6 — Frontend Dashboard
- [x] React 18 + Vite + TypeScript application scaffolded
- [x] Bespoke dark-mode CSS design system (`frontend/src/index.css`)
- [x] Data Ingestion & Cleaning Summary view (`frontend/src/views/UploadView.tsx`)
- [x] Behavioral Segments & RFM Profiles view (`frontend/src/views/SegmentsView.tsx`)
- [x] Campaign Recommendations & WhatsApp Chat Preview modal (`frontend/src/views/RecommendationsView.tsx`)
- [x] Clustering Metrics & Mathematical Validation view (`frontend/src/views/MetricsView.tsx`)
- [x] Sidebar navigation with real-time backend API health status (`frontend/src/components/Sidebar.tsx`)

### ✅ MILESTONE 7 — Automated Verification & Tests
- [x] `backend/tests/test_ingestion.py` — Ingestion & anomaly tests
- [x] `backend/tests/test_rfm.py` — RFM calculations tested against hand-verified formulas
- [x] `backend/tests/test_clustering.py` — Clustering boundaries and metric tests
- [x] `backend/tests/test_fatigue.py` — Consent, suppression, and frequency cap tests
- [x] `backend/tests/test_recommendations.py` — Recommendation scoring and explanation tests

### ✅ MILESTONE 8 — College Review Deliverables
- [x] **College Topic Submission Guide** (`docs/COLLEGE_FORM_SUBMISSION.md`) with copy-paste answers for [Google Form](https://forms.gle/NkjP6Ww7BjubVnqk6)
- [x] **Research Paper Draft** (`docs/RESEARCH_PAPER_DRAFT.md`) in IEEE format with 10 real, verified citations
- [x] **Presentation Deck Outline & Script** (`docs/PRESENTATION_SLIDES.md`)
- [x] **Presentation PPTX Generator** (`backend/scripts/generate_presentation.py`)
- [x] **Review Demonstration Script** (`docs/DEMO_SCRIPT.md`)
- [x] **Viva Voce & Technical Defense Preparation** (`docs/VIVA_PREPARATION.md`)

---

## Deliverables Summary Matrix

| Review Requirement | Document / File | Status |
|---|---|---|
| **College Topic Form** | [`docs/COLLEGE_FORM_SUBMISSION.md`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/docs/COLLEGE_FORM_SUBMISSION.md) | Ready to Submit |
| **Research Paper Draft** | [`docs/RESEARCH_PAPER_DRAFT.md`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/docs/RESEARCH_PAPER_DRAFT.md) | Ready for Review |
| **IEEEtran Paper Source** | [`docs/RESEARCH_PAPER_DRAFT.tex`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/docs/RESEARCH_PAPER_DRAFT.tex) | Compiles Successfully |
| **Presentation Deck** | [`docs/PRESENTATION_SLIDES.md`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/docs/PRESENTATION_SLIDES.md) | Ready to Present |
| **Demonstration Script** | [`docs/DEMO_SCRIPT.md`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/docs/DEMO_SCRIPT.md) | Ready to Rehearse |
| **Viva Voce Prep** | [`docs/VIVA_PREPARATION.md`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/docs/VIVA_PREPARATION.md) | Ready to Study |
| **Backend Implementation** | [`backend/`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/backend/) | Complete & Tested |
| **Frontend Dashboard** | [`frontend/`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/frontend/) | Complete & Connected |
| **System Architecture** | [`docs/ARCHITECTURE.md`](file:///c:/Users/Sarth/Documents/GitHub/Final-Year-Project/docs/ARCHITECTURE.md) | Documented |

## Known Code and Documentation Discrepancies

- `README.md` references `backend.scripts.init_db`, but that script is not present.
- Older architecture text listed campaign routes that are not registered by `backend/main.py`.
- The active frontend displays RFM score denominators as `/5`, while the current backend scoring output is based on four bins.
- The segment filter control is present in the frontend but currently does not filter the customer table.
- The frontend WhatsApp preview is a UI simulation; it does not create a persisted `MessageEvent` or invoke the backend adapter.
