# Viva Voce & Technical Defense Preparation Guide

**Project Title:** AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform  
**Target Review:** Second Review & Viva Voce Examination  
**Degree:** B.E. Information Technology

---

## Category 1: Machine Learning & Analytics Questions

### Q1: Why did you choose K-Means instead of DBSCAN or Hierarchical Clustering?
**Answer:**
- **K-Means:** K-Means operates in $O(N \cdot K \cdot d \cdot i)$ time, making it exceptionally scalable for retail transaction datasets containing hundreds of thousands of customer vectors. Centroids provide intuitive, explainable reference points (median recency, frequency, and monetary spend) that can be directly mapped to marketing strategies.
- **Why not DBSCAN?** DBSCAN clusters based on density and labels outliers as noise (cluster -1). In retail customer relationship management, every customer must be categorized into an actionable marketing cohort rather than discarded as noise. Moreover, density variations between regular buyers and high-net-worth VIPs make global $\epsilon$ selection suboptimal.
- **Why not Hierarchical/Agglomerative?** Hierarchical clustering has $O(N^2)$ to $O(N^3)$ computational and memory complexity, which does not scale to large retail customer bases.

---

### Q2: Why did you apply log-transformation and Z-score scaling before clustering?
**Answer:**
- **Skewness Correction:** In real retail datasets (such as the UCI Online Retail benchmark), Monetary spend and Frequency exhibit extreme positive skewness (Power Law / Pareto distribution), where 80% of transactions are low-value and a few outliers spend tens of thousands of dollars.
- **Euclidean Distance Distortion:** K-Means relies on Euclidean distance:
  $$d(p, q) = \sqrt{\sum (p_i - q_i)^2}$$
  If monetary values are in thousands of dollars while frequency is single digits, monetary spend will completely dominate the distance metric, rendering frequency and recency irrelevant.
- **Solution:** We apply $x' = \ln(x + 1)$ to compress heavy tails and stabilize variance, followed by standard Z-score scaling:
  $$z = \frac{x' - \mu}{\sigma}$$
  so each feature has zero mean and unit variance.

---

### Q3: How did you select the optimal number of clusters ($K$)?
**Answer:**
We avoided arbitrary human selection by implementing an automated multi-metric evaluation loop sweeping $K \in [2, 10]$:
1. **Silhouette Coefficient (Rousseeuw, 1987):** Evaluates whether an instance is closer to its own cluster than neighboring clusters. Scores range from -1 to +1. Our peak score was achieved at $K=4$ (0.4328).
2. **Davies–Bouldin Index:** Measures cluster separation based on the ratio of within-cluster scatter to between-cluster separation. Lower is better. $K=4$ yielded the minimum DBI (0.8712).
3. **Calinski–Harabasz Index (Variance Ratio Criterion):** Measures the ratio of between-cluster dispersion to within-cluster dispersion.
Together, these indices validated that 4 clusters represented the optimal balance between granularity and cluster cohesion.

---

### Q4: What does a Silhouette Score of ~0.43 mean? Is that good enough?
**Answer:**
Yes. In natural behavioral and social science datasets (unlike synthetic Gaussian blobs), consumer behavior is continuous rather than strictly disjoint. Academic literature (e.g., Chen et al., 2012 on the UCI benchmark) establishes that real-world retail RFM clustering typically achieves Silhouette scores between 0.35 and 0.45. A score of 0.43 confirms strong cluster separation without artificial over-fitting.

---

## Category 2: Architecture & System Engineering Questions

### Q5: Explain your backend architecture and separation of concerns.
**Answer:**
Our backend adheres to clean, layered architecture:
- **Routers (`backend/routers/`):** Handle HTTP request/response routing, status codes, and input parsing.
- **Services (`backend/services/`):** Pure business logic isolated from HTTP frameworks (e.g. `ingestion.py`, `rfm.py`, `clustering.py`, `fatigue.py`, `recommendations.py`).
- **Schemas (`backend/schemas/`):** Pydantic v2 data transfer objects ensuring strict type safety and request validation.
- **Models (`backend/models/`):** SQLAlchemy ORM entities representing relational tables in SQLite.
- **Adapters (`backend/adapters/`):** Ports-and-adapters design pattern for external services (e.g. `WhatsAppAdapter` interface implemented by `MockWhatsAppAdapter` and `LiveWhatsAppAdapter`).

---

### Q6: Why did you build a Mock WhatsApp Adapter?
**Answer:**
- **Academic & Operational Reality:** Live WhatsApp Cloud API messaging requires an active Meta Business Account, verified organization phone number, approved message templates, and incurs per-conversation utility fees payable to Meta.
- **Architectural Design:** We implemented an abstracted interface (`WhatsAppAdapterBase`). During development and review, the system uses `MockWhatsAppAdapter`, which logs dispatches, verifies payload structure, checks rate limits, and simulates delivery statuses (`sent`, `delivered`, `read`) with explicit `[SIMULATED]` badges.
- **Plug-and-Play Transition:** To switch to production, only the environment variables (`WHATSAPP_API_TOKEN`, `PHONE_NUMBER_ID`) need to be supplied to `LiveWhatsAppAdapter`—zero core application logic needs rewriting.

---

## Category 3: Marketing Fatigue & Privacy Questions

### Q7: What is Marketing Fatigue, and how does your engine prevent it?
**Answer:**
- **Definition:** Marketing fatigue occurs when consumers are inundated with excessive, repetitive, or irrelevant promotional messages, triggering psychological reactance, lower brand affinity, and immediate unsubscribes/spam reports.
- **Our Prevention Engine:** Before any campaign recommendation is approved, it must pass through sequential boolean gates:
  1. **Consent Check:** Verifies explicit customer opt-in (`consent_given == True`).
  2. **Suppression List Check:** Ensures customer has not opted out or requested deletion (`suppressed == False`).
  3. **Frequency Capping:** Enforces a rolling threshold (maximum 3 messages per customer per 30-day window).
  4. **Recency Window Eligibility:** Ensures messages match the customer's purchase lifecycle (e.g. Win-Back campaigns are only sent to customers whose recency exceeds 30 days).

---

### Q8: How does your system comply with data privacy regulations (e.g., GDPR / DPDP Act 2023)?
**Answer:**
1. **Consent Gating:** Automated blocking of customers who have not granted affirmative consent.
2. **Right to Withdraw / Suppression:** Instant exclusion upon suppression flag update.
3. **Data Minimization:** Only transaction-level metadata (invoices, dates, quantities, amounts) is processed—no sensitive personally identifiable information (PII) like passwords or credit cards is stored in the feature engineering tables.
4. **Audit Logging:** Every rejection logs the exact policy rule violated for governance auditing.

---

## Category 4: Software Quality & Testing Questions

### Q9: How did you test your implementation?
**Answer:**
We built a comprehensive automated test suite using `pytest`:
- **`test_ingestion.py`:** Tests CSV edge cases including missing customer IDs, invalid date strings, negative unit prices, negative quantities, duplicate rows, and cancellation invoice parsing (prefix 'C').
- **`test_rfm.py`:** Tested against **hand-verified mathematical calculations** with fixed reference dates to guarantee that Recency, Frequency (unique invoices), Monetary totals, and quintile scores are exact.
- **`test_clustering.py`:** Verifies cluster assignment dimensions, metric boundaries (Silhouette $\in [-1, 1]$, DBI $\ge 0$), and reproducibility with `random_seed=42`.
- **`test_fatigue.py`:** Explicitly tests `consent=False`, `suppressed=True`, frequency saturation (>3 messages), and campaign-specific recency window filters.
- **`test_recommendations.py`:** Verifies recommendation completeness, score bounds (0–100), and non-null explanation strings.
