# Project Plan — AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform

**Project Title:** AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform  
**Degree:** BE Information Technology  
**Second Review Deadline:** 19–24 October 2026  
**Team Size:** 4 members (roles TBD)

---

## Research Question

> How can RFM-based customer segmentation, explainable marketing-fatigue rules, and consent-aware eligibility checks be combined into an auditable workflow for recommending customer marketing campaigns?

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
| 1 | Backend skeleton: FastAPI + SQLAlchemy + health endpoint | A | 🔄 In Progress |
| 2 | CSV ingestion service + validation + example dataset | A | 🔄 In Progress |
| 3 | RFM feature engineering + K-Means clustering + evaluation metrics | A | 🔄 In Progress |
| 4 | Fatigue rules + consent eligibility + campaign recommendations | A | 🔄 In Progress |
| 5 | FastAPI endpoints for all services | A | 🔄 In Progress |
| 6 | React frontend: upload → analysis → segments → recommendations | A | 🔄 In Progress |
| 7 | Automated tests (pytest) | A | 🔄 In Progress |
| 8 | Research paper draft | A | ⏳ Pending |
| 9 | Review presentation and demonstration materials | A | ⏳ Pending |
| 10 | Database persistence + multi-tenancy | B | ⏳ Pending |
| 11 | WhatsApp adapter (mock + live skeleton) | B | ⏳ Pending |
| 12 | Live WhatsApp sending (requires credentials) | C | 🔒 Blocked |

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
