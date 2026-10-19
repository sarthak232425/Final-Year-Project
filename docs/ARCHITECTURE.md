# Architecture — AI Customer Segmentation & WhatsApp Marketing Platform

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/Vite)                    │
│  Upload → Dashboard → Segments → Recommendations → Campaigns     │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP (REST JSON)
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI / Python)                     │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────┐  │
│  │ Ingestion│  │   RFM    │  │Clustering│  │Recommendations│  │
│  │ Service  │→ │ Service  │→ │ Service  │→ │   Service     │  │
│  └──────────┘  └──────────┘  └──────────┘  └───────────────┘  │
│       │                                             │            │
│  ┌──────────┐                              ┌────────────────┐   │
│  │ Fatigue  │                              │   WhatsApp     │   │
│  │  Rules   │                              │   Adapter      │   │
│  └──────────┘                              │ (Mock/Live)    │   │
│                                            └────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │ SQLAlchemy ORM
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE (SQLite dev / PostgreSQL prod)              │
│  Tenants │ Customers │ Transactions │ Segments │ Campaigns │...  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

```
CSV Upload
    │
    ▼
Validation & Cleaning
  • Missing customer_id → drop + log
  • Invalid date → drop + log
  • Negative/zero quantity → drop + log
  • Cancellation invoices (C prefix) → exclude from RFM
  • Duplicate (invoice_id, customer_id) → deduplicate
    │
    ▼
RFM Feature Engineering (per customer)
  Recency  = (reference_date − max(invoice_date)).days
  Frequency = count(distinct invoice_id)
  Monetary  = sum(quantity × unit_price) for valid transactions
    │
    ▼
Preprocessing (before clustering)
  • Log-transform Monetary (right-skewed)
  • RobustScaler on [R, F, M_log]
    │
    ▼
K-Means Clustering
  • K range: 2–10 (or 2–min(10, n_customers−1))
  • Random seed: 42
  • Evaluate: Silhouette, Davies-Bouldin, Calinski-Harabasz
  • Select K by Silhouette
    │
    ▼
Segment Labelling (dynamic, data-driven)
  • Compare cluster medians vs dataset medians
  • Assign descriptive label from cluster characteristics
    │
    ▼
Fatigue & Eligibility Check (per customer)
  • consent_given = True? (else BLOCKED: no consent)
  • suppressed = False? (else BLOCKED: suppressed)
  • messages_last_30_days < frequency_cap? (else BLOCKED: fatigue)
  • last_purchase recency check (segment-dependent)
    │
    ▼
Campaign Recommendation
  • Match segment + eligibility → campaign type
  • Attach explanation text + supporting data fields
    │
    ▼
Dashboard Display / WhatsApp Adapter
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| POST | /api/v1/ingest/upload | Upload CSV file |
| GET | /api/v1/ingest/status | Last ingestion status |
| POST | /api/v1/analysis/run | Run RFM + clustering |
| GET | /api/v1/analysis/rfm | Get RFM results |
| GET | /api/v1/analysis/metrics | Get clustering metrics |
| GET | /api/v1/segments | List all segments |
| GET | /api/v1/segments/{id}/customers | Customers in segment |
| GET | /api/v1/recommendations | Get all recommendations |
| GET | /api/v1/recommendations/{customer_id} | Customer recommendation |
| POST | /api/v1/campaigns/preview | Preview campaign recipients |
| GET | /api/v1/campaigns | List campaigns |

---

## Database Entity Relationship Diagram

```
TENANT (1) ──< USER
   │
   └──< CUSTOMER (1) ──< TRANSACTION
            │
            ├── CUSTOMER_SCORE (RFM)
            │
            └── CAMPAIGN_RECIPIENT >── CAMPAIGN >── MESSAGE_EVENT
                                           │
                                       RECOMMENDATION
```

### Table Definitions

**tenant** — `id, name, created_at`  
**user** — `id, tenant_id, email, hashed_password, role, created_at`  
**customer** — `id, tenant_id, external_id, consent_given, suppressed, last_contact_date, messages_last_30_days, created_at`  
**transaction** — `id, tenant_id, customer_id, invoice_id, invoice_date, quantity, unit_price, line_total, is_cancellation, created_at`  
**customer_score** — `id, customer_id, recency_days, frequency, monetary, r_score, f_score, m_score, rfm_score, segment_label, cluster_id, run_id, created_at`  
**segment** — `id, tenant_id, run_id, cluster_id, label, size, median_recency, median_frequency, median_monetary, created_at`  
**campaign** — `id, tenant_id, name, campaign_type, target_segment_id, status, created_at`  
**campaign_recipient** — `id, campaign_id, customer_id, eligible, ineligibility_reason, recommendation_explanation, created_at`  
**message_event** — `id, campaign_id, customer_id, wa_message_id, status, sent_at, delivered_at, read_at, failed_at, failure_reason, is_simulated`  
**recommendation** — `id, customer_id, run_id, campaign_type, score, explanation, supporting_data, created_at`

---

## WhatsApp Adapter Design

```python
class WhatsAppAdapter(ABC):
    def send_message(self, to: str, template: str, params: dict) -> MessageResult: ...
    def get_status(self, message_id: str) -> MessageStatus: ...

class MockWhatsAppAdapter(WhatsAppAdapter):
    """Always returns SIMULATED results. Safe for development."""

class LiveWhatsAppAdapter(WhatsAppAdapter):
    """Requires WHATSAPP_TOKEN + WHATSAPP_PHONE_NUMBER_ID in .env
       Only active when WHATSAPP_LIVE_MODE=true"""
```

---

## Configuration

All secrets via `.env` file. See `backend/.env.example`.  
Never commit `.env` to version control.

```
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=...
WHATSAPP_LIVE_MODE=false
WHATSAPP_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_WEBHOOK_VERIFY_TOKEN=
```

---

## Technology Versions (pinned)

| Package | Version |
|---------|---------|
| Python | 3.11+ |
| FastAPI | 0.115.x |
| SQLAlchemy | 2.0.x |
| pandas | 2.2.x |
| scikit-learn | 1.5.x |
| numpy | 1.26.x |
| pydantic | 2.x |
| uvicorn | 0.30.x |
| pytest | 8.x |
| Node.js | 20 LTS |
| React | 18.x |
| Vite | 5.x |
| TypeScript | 5.x |
