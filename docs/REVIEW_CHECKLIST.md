# Second Review Checklist — 19–24 October 2026

**Instructions:** Tick each item only when it is demonstrably working, not merely coded.

---

## Priority A — Must Be Done for Review

### Implementation
- [x] Repository is clean and cloneable
- [x] Backend starts with `uvicorn backend.main:app --reload`
- [x] Frontend starts with `npm run dev`
- [x] GET /health returns 200 OK
- [x] CSV upload endpoint accepts file and returns cleaning summary
- [x] Example dataset ships with repo (`backend/data/example_transactions.csv`) and loads without error
- [x] RFM features calculated correctly (verified against hand calculations)
- [x] K-Means clustering runs on real data
- [x] Silhouette Score reported (0.4328 at K=4)
- [x] Davies–Bouldin Index reported (0.8712 at K=4)
- [x] Calinski–Harabasz Score reported (194.70 at K=4)
- [x] Segment labels generated dynamically from cluster statistics
- [x] Fatigue rules enforce frequency cap (max 3 messages / 30d)
- [x] Consent check blocks ineligible customers (`consent_given=False`)
- [x] Campaign recommendations generated with explanation text
- [x] Dashboard displays real data from backend (not mocked)
- [x] At least one end-to-end workflow is demonstrable (Upload -> RFM -> Clusters -> Recommendations -> WhatsApp Preview)

### Testing
- [x] All pytest tests pass (`pytest backend/tests/ -v`)
- [x] RFM tests include hand-verified examples (`backend/tests/test_rfm.py`)
- [x] Ingestion tests cover invalid CSV inputs (`backend/tests/test_ingestion.py`)
- [x] Fatigue tests cover consent=False and suppressed=True cases (`backend/tests/test_fatigue.py`)
- [x] Test coverage exceeds core requirements

### Documentation
- [x] README.md includes working setup commands
- [x] .env.example is present and complete (`backend/.env.example`)
- [x] ARCHITECTURE.md explains data flow (`docs/ARCHITECTURE.md`)
- [x] All design decisions documented in PROJECT_PLAN.md (`docs/PROJECT_PLAN.md`)

---

## Priority A — Research Paper Draft

- [x] Paper draft written (`docs/RESEARCH_PAPER_DRAFT.md`)
- [x] Abstract written
- [x] Introduction written
- [x] Problem statement written
- [x] Literature review written (≥ 10 verified references)
- [x] All references verified (Hughes 1994, MacQueen 1967, Rousseeuw 1987, Davies-Bouldin 1979, Calinski-Harabasz 1974, Chen et al. 2012, Fader et al. 2005, Godfrey et al. 2011, Kumar & Reinartz 2016, Verhoef et al. 2015)
- [x] Methodology section describes actual implementation
- [x] Experimental setup documents dataset, preprocessing, K selection
- [x] Preliminary results contain actual measured metrics (Silhouette, DBI, CHI)
- [x] Results distinguish: real dataset vs synthetic vs designed-but-not-tested
- [x] Limitations section is honest
- [x] Conclusion and future work written

---

## Priority A — Review Presentation

- [x] Presentation deck exists (`docs/PRESENTATION_SLIDES.md` and generator `backend/scripts/generate_presentation.py`)
- [x] Contains genuine implementation metrics and architecture
- [x] Contains actual clustering metric tables and evaluation sweep
- [x] Architecture diagram included in documentation and slides
- [x] Demonstration script exists (`docs/DEMO_SCRIPT.md`)
- [x] Viva Q&A preparation document exists (`docs/VIVA_PREPARATION.md`)
- [x] Final topic text file ready for college form submission (`docs/COLLEGE_FORM_SUBMISSION.md`)

---

## Priority B — After Core Works

- [x] SQLite database stores results persistently (`backend/database.py`, `backend/models/`)
- [ ] Multi-tenant data isolation enforced in backend queries
- [x] WhatsApp mock adapter runs with SIMULATED label (`backend/adapters/whatsapp.py`)
- [ ] Webhook event deduplication implemented

---

## Priority C — After Review

- [ ] Live WhatsApp sending with verified credentials
- [ ] Advanced recommendation model (Contextual Multi-Armed Bandits)
- [ ] CRM/POS integrations (Shopify, WooCommerce)
- [ ] Production cloud deployment

---

## Verification Commands

```powershell
# Run backend tests
pytest backend\tests\ -v

# Start backend server
uvicorn backend.main:app --reload --port 8000

# Check health endpoint
curl http://localhost:8000/health

# Start frontend application
cd frontend
npm install
npm run dev
```
