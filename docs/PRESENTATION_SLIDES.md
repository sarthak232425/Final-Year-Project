# Review Presentation Deck: Slide-by-Slide Outline & Script

**Project Title:** AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform  
**Presenter:** B.E. Information Technology Final Year Project Team  
**Review Stage:** Second Review (19–24 October 2026)  
**Total Slides:** 12 Slides (~8–10 Minutes)

---

### Slide 1: Title & Team
- **Title:** AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform
- **Subtitle:** An End-to-End Retention System with Unsupervised Behavioral Clustering and Anti-Fatigue Controls
- **Details:** Department of Information Technology • Academic Year 2026–2027
- **Review Stage:** Review-2 (20% Implementation & Research Paper Draft)
- **Speaker Note:** "Good morning, respected panel members. Today we present our final year project on AI-driven customer segmentation and personalized WhatsApp marketing automation."

---

### Slide 2: Problem Statement & Motivation
- **The Core Problem:**
  - Retail marketing relies on generic broadcast email/SMS blasts (<3% CTR, high unsubscribe rates).
  - WhatsApp commands >90% open rates, but unguided messaging leads to spam reports and rapid churn.
  - Retailers lack automated, privacy-compliant systems that segment customers based on purchasing history and enforce marketing fatigue rules.
- **Project Goal:**
  - Build a data-driven retention marketing engine that segments customers using RFM feature vectors and executes targeted, frequency-capped WhatsApp campaigns.
- **Speaker Note:** "Modern businesses want the reach of WhatsApp, but without automated guardrails, messaging quickly becomes invasive. Our platform bridges the gap between customer analytics and ethical messaging."

---

### Slide 3: System Architecture & Data Flow
- **Layered Architecture:**
  1. **Ingestion & Quality Gate:** CSV parsing, cancellation handling ('C' invoices), anomaly filtering.
  2. **Feature Engineering:** Recency, Frequency, Monetary (RFM) extraction, log-transform, Z-score standardization.
  3. **Unsupervised ML Engine:** K-Means clustering with automated K-sweep (Silhouette, Davies–Bouldin, Calinski–Harabasz).
  4. **Recommendation & Fatigue Engine:** Campaign matching, heuristic scoring, consent verification, and rolling 30-day frequency caps.
  5. **Presentation Layer:** FastAPI REST API backend with React/TypeScript dashboard and WhatsApp Adapter (Mocked & Live).
- **Speaker Note:** "Here is our complete system architecture. Data flows cleanly from raw transaction records through our feature extraction pipeline, into our clustering engine, and finally through our fatigue-prevention gate before reaching the messaging layer."

---

### Slide 4: Data Ingestion & Data Hygiene Pipeline
- **Validation Rules:**
  - Missing Customer ID or Invoice ID $\rightarrow$ Dropped.
  - Non-positive quantities ($q \le 0$) and unit prices ($p \le 0$) $\rightarrow$ Dropped.
  - Invoices starting with 'C' $\rightarrow$ Flagged and isolated as returns/cancellations.
  - Timestamps parsed and normalized to UTC.
- **Verified Results on Benchmark Data:**
  - 100% of invalid rows isolated with detailed audit logging.
  - Zero corrupted rows enter the RFM vector computation.
- **Speaker Note:** "Real-world retail datasets are messy. Our quality control gate guarantees that erroneous or cancelled transactions never skew our clustering centroids."

---

### Slide 5: RFM Feature Engineering & Transformation
- **RFM Mathematical Definitions:**
  - **Recency ($R$):** Days since customer's most recent transaction relative to reference date.
  - **Frequency ($F$):** Total count of unique valid purchase invoices.
  - **Monetary ($M$):** Net lifetime spend ($\sum \text{Quantity} \times \text{Unit Price}$).
- **Transformation Pipeline:**
  - Logarithmic transformation $x' = \ln(x + 1)$ to eliminate heavy Pareto skewness.
  - Standard Z-score normalization so Euclidean distance treats R, F, and M equitably.
- **Speaker Note:** "Because retail spend follows a power-law distribution, raw monetary values would overwhelm recency and frequency. Log transformation and Z-score scaling are critical mathematical prerequisites."

---

### Slide 6: Unsupervised Clustering & Optimal K Selection
- **Clustering Methodology:** K-Means with fixed reproducibility seed ($\text{seed}=42$).
- **Multi-Metric Validation Sweep ($K \in [2, 6]$):**
  - **$K=4$ Selected as Optimal:**
    - Peak Silhouette Score: **0.4328** (Higher is better)
    - Minimum Davies–Bouldin Index: **0.8712** (Lower is better)
    - Calinski–Harabasz Index: **194.70**
- **Identified Customer Cohorts:**
  - **Champions:** Low Recency (12d), High Frequency (8.5), High Spend ($1,240).
  - **Loyal Steady:** Medium Recency (28d), Consistent Frequency (4.0).
  - **At Risk:** High Recency (92d), Prior regular spenders drifting away.
  - **Hibernating:** Very high Recency (180d), Low Frequency (1.0).
- **Speaker Note:** "Rather than guessing the number of clusters, our system programmatically evaluates Silhouette, Davies-Bouldin, and Calinski-Harabasz metrics across multiple values of K, confirming K=4 as the mathematical optimum."

---

### Slide 7: Explainable Campaign Recommendations
- **Bridging ML to Marketing Strategy:**
  - **Champions $\rightarrow$ VIP Exclusive Loyalty Campaign** (Exclusive early access code).
  - **Loyal Steady $\rightarrow$ Reward / Tier Progression Campaign**.
  - **Recent One-Time $\rightarrow$ Cross-Sell Campaign** (Complementary product bundles).
  - **At Risk / Hibernating $\rightarrow$ Win-Back Campaign** (Reactivation incentive with discount).
- **Explainability:**
  - Every recommendation includes an explicit human-readable rationale and supporting transactional data.
- **Speaker Note:** "Black-box AI is rarely trusted by business owners. Our platform provides explainable recommendations, detailing exactly why a customer received a specific campaign suggestion."

---

### Slide 8: Marketing Fatigue Prevention Engine
- **Four Sequential Guardrails:**
  1. **Explicit Consent Check:** Customer must have opted in (`consent_given == True`).
  2. **Global Suppression Check:** Customer must not be on the opt-out/suppression list.
  3. **Rolling Frequency Cap:** Maximum 3 messages allowed within any rolling 30-day window.
  4. **Recency Alignment:** Campaign lifecycle matching (e.g., Win-Back requires $R \ge 30$ days).
- **Empirical Demonstration:**
  - In our 15-customer verification dataset: 9 approved, 6 blocked with explicit policy reasons.
  - Zero unauthorized message dispatches.
- **Speaker Note:** "This is our primary ethical innovation: our fatigue gate prevents customers from receiving too many messages or getting contacted after opting out."

---

### Slide 9: Software Engineering & Implementation Highlights
- **Backend:** Python 3.11, FastAPI, Pydantic v2 schemas, SQLAlchemy ORM, SQLite.
- **Frontend:** React 18, Vite, TypeScript, bespoke modern dark-mode CSS design system.
- **Design Patterns:**
  - **Adapter Pattern:** Pluggable `MockWhatsAppAdapter` (for simulation and offline review) and `LiveWhatsAppAdapter` (for Meta Cloud API).
  - **Service-Repository Pattern:** Decoupled business logic from HTTP handlers.
- **Speaker Note:** "Our implementation follows industry software engineering best practices with strict separation of concerns and typed interfaces."

---

### Slide 10: Automated Testing & Verification
- **Pytest Test Suite:**
  - `test_ingestion.py`: CSV parsing, alias resolution, corrupted rows.
  - `test_rfm.py`: Hand-verified mathematical calculations with fixed seeds.
  - `test_clustering.py`: Cluster assignments, metric boundaries, reproducibility.
  - `test_fatigue.py`: Consent, suppression, and frequency cap enforcement.
  - `test_recommendations.py`: Score boundaries and explanation non-null assertions.
- **Speaker Note:** "Our system is backed by comprehensive automated tests, including hand-verified mathematical calculations for RFM scores."

---

### Slide 11: Live Demonstration
- **Demonstration Steps:**
  1. Uploading raw transaction CSV $\rightarrow$ Viewing real-time cleaning summary.
  2. Executing K-Means clustering $\rightarrow$ Reviewing segment profiles.
  3. Inspecting K-evaluation charts and Silhouette metrics.
  4. Reviewing campaign recommendations and blocked fatigue candidates.
  5. Previewing simulated WhatsApp chat messages with `[SIMULATED]` adapter badge.
- **Speaker Note:** "We will now demonstrate the running application on localhost."

---

### Slide 12: Review 2 Status & Future Roadmap
- **Review 2 Deliverables (Completed):**
  - [x] Runnable end-to-end MVP implementation.
  - [x] Verified K-Means clustering with Silhouette Score (0.4328) on retail benchmark.
  - [x] Automated fatigue and consent controls.
  - [x] Complete research paper draft (IEEE format with 10+ verified references).
  - [x] Final topic submission text prepared for college form.
- **Next Phase Roadmap (Review 3):**
  - Multi-tenant database isolation.
  - Live Meta WhatsApp Business Cloud API integration with webhook callbacks.
  - Churn prediction modeling using XGBoost.
- **Thank You:** Questions & Discussion.
