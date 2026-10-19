# Project Review Demonstration Script

**Project Title:** AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform  
**Target Audience:** Internal/External College Review Panel  
**Estimated Time:** 7–10 Minutes

---

## Pre-Demo Checklist (2 Minutes Before Panel Arrives)
- [ ] Terminal 1: Backend running (`uvicorn backend.main:app --reload --port 8000`)
- [ ] Terminal 2: Frontend running (`npm run dev` in `frontend/`)
- [ ] Browser window 1 opened at: `http://localhost:5173`
- [ ] Browser window 2 opened at: `http://localhost:8000/docs` (FastAPI Swagger UI as backup)
- [ ] Sample CSV file `backend/data/example_transactions.csv` ready on desktop/folder.

---

## Step-by-Step Demonstration Flow

### Step 1: System Overview & Architecture (1.5 Minutes)
- **What to show:** Open the web dashboard homepage (`http://localhost:5173`).
- **What to say:**
  > "Good morning, respected professors. Our project is an end-to-end intelligent customer retention platform. While conventional marketing relies on broadcast email blasts with low open rates, conversational platforms like WhatsApp have open rates exceeding 90%. However, without behavioral targeting and anti-fatigue controls, customers feel spammed and opt out.
  >
  > Our platform solves this in three coordinated steps:
  > 1. Ingesting and cleaning raw retail transactional records;
  > 2. Performing unsupervised RFM feature clustering with mathematical validation;
  > 3. Generating explainable campaign recommendations governed by an automated anti-fatigue gate."

### Step 2: Data Ingestion & Quality Control (2 Minutes)
- **What to show:**
  - Navigate to the **"Data Ingestion"** tab.
  - Click the **"📂 Load Example Dataset"** button (or drag & drop `example_transactions.csv`).
  - Point out the **Data Cleaning & Validation Summary** card that appears immediately.
- **What to say:**
  > "Here, our ingestion pipeline accepts raw transactional data. Notice that out of 24 submitted records, 19 valid transactions were retained, 1 cancellation was isolated, and 4 corrupt records were safely dropped.
  >
  > In the issue breakdown table, we demonstrate strict data hygiene: rows with missing Customer IDs, negative unit prices, negative quantities, or invalid date strings are rejected before they can distort the mathematical feature vectors."

### Step 3: Running Unsupervised RFM Clustering (2 Minutes)
- **What to show:**
  - Click the **"⚡ Run RFM & Clustering"** button.
  - The dashboard automatically transitions to the **"RFM & Segments"** tab.
  - Scroll through the generated segment cards (Champions, Loyal Customers, At Risk, Hibernating).
  - Scroll down to the **Customer RFM Feature Vectors** table showing individual R, F, and M percentiles.
- **What to say:**
  > "Once the pipeline executes, the system transforms raw invoices into Recency, Frequency, and Monetary (RFM) vectors. Because retail spend has a heavy right tail, we apply logarithmic transformation followed by Z-score standardization.
  >
  > Our K-Means model partitions the customer base into distinct cohorts. Rather than using arbitrary labels, our algorithm dynamically assigns behavioral labels based on centroid percentiles:
  > - High frequency, high monetary, low recency are labeled *Champions*;
  > - Customers who have not ordered in months are labeled *At Risk* or *Hibernating*."

### Step 4: Model Validation & Statistical Metrics (1.5 Minutes)
- **What to show:**
  - Click on the **"Model Metrics"** tab on the sidebar.
  - Highlight the four core metric cards:
    - Optimal K = 4
    - Silhouette Score = 0.4328
    - Davies–Bouldin Index = 0.8712
    - Calinski–Harabasz Index = 194.70
  - Show the bar chart of the K evaluation sweep (K = 2 to 10).
- **What to say:**
  > "Rather than guessing the number of clusters, our system programmatically sweeps K from 2 to 10 with a reproducible random seed (seed=42).
  >
  > As shown in this chart, K=4 achieves the peak Silhouette Score of 0.4328 and the lowest Davies–Bouldin Index (0.8712). In academic literature, a Silhouette score above 0.40 on transactional retail data confirms dense, well-separated clusters."

### Step 5: Explainable Recommendations & Marketing Fatigue Guardrails (2 Minutes)
- **What to show:**
  - Click on the **"Recommendations"** tab.
  - Point out the top counters: Total Audience vs Approved for Outreach vs Blocked/Fatigued.
  - Click the **"Ineligible"** filter button to show blocked customers.
  - Expand the **Fatigue & Policy Verifications** checklist on an ineligible customer (e.g. showing `Consent Check: FAILED` or `Frequency Cap: EXCEEDED (4/3 messages in 30d)`).
  - Click back to **"Eligible"** and click **"💬 Preview WhatsApp Message"** on an approved customer.
  - Show the simulated WhatsApp chat modal with template text and the `[SIMULATED ADAPTER]` badge.
- **What to say:**
  > "Finally, we bridge machine learning into actionable marketing. For every customer, our engine suggests an appropriate campaign archetype—such as VIP Loyalty or Win-Back—paired with human-readable rationale.
  >
  > Crucially, we enforce our **Marketing Fatigue Engine**:
  > - If a customer has not opted in (`consent=False`), they are blocked.
  > - If a customer is on the global suppression list, they are blocked.
  > - If a customer has already received 3 messages in the past 30 days, they are blocked to prevent inbox spam.
  >
  > Clicking 'Preview WhatsApp Message' displays the rendered message template. We have architected this using an Adapter design pattern: during review, it runs safely on our `MockWhatsAppAdapter` with clear simulated badges, ready to plug into Meta's live Cloud API once production credentials are provisioned."

### Step 6: Conclusion & Viva Transition (30 Seconds)
- **What to say:**
  > "To summarize: our implementation is modular, fully tested with unit and integration tests covering edge cases, and satisfies both machine learning rigor and real-world marketing ethics. We are happy to answer any questions from the panel."
