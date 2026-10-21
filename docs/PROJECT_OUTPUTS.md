# Empirical Project Outputs & Execution Data
**Project Title:** AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform  
**Environment:** Python 3.14.7 | FastAPI 0.115 | Scikit-Learn 1.6 | Vite 5.4 | React 18.3
**Dataset Evaluated:** `backend/data/example_transactions.csv` (57 records)

---

## 1. Automated Verification Test Suite (Pytest)

```text
============================= test session starts =============================
platform win32 -- Python 3.14.7, pytest-9.1.1
rootdir: C:/Users/Sarth/Documents/GitHub/Final-Year-Project
collected 87 items

backend/tests/test_clustering.py ......                                  [ 17%]
backend/tests/test_fatigue.py ....................                       [ 39%]
backend/tests/test_ingestion.py .........................                [ 66%]
backend/tests/test_recommendations.py ..............                     [ 81%]
backend/tests/test_rfm.py ................                               [100%]

============================= 87 passed in 2.38s ==============================
```

## 2. Data Ingestion & Quality Control Outputs

### 2.1 Ingestion Summary Card
| Ingestion Metric | Count | Operational Impact |
| :--- | :---: | :--- |
| **Original Raw Rows** | **57** | Total transactional entries in uploaded CSV |
| **Valid Invoices Retained** | **52** | Parsed, normalized, and ready for feature calculation |
| **Cancellations Isolated** | **2** | Tagged as cancellations (`is_cancellation=True`); excluded from RFM |
| **Dropped Corrupt Rows** | **5** | Removed due to failing structural integrity constraints |
| **Deduplicated Lines** | **1** | Identical invoice lines consolidated |

### 2.2 Rejection & Data Hygiene Log
| Row # | Rejected Column | Offending Value | Quality Rule Violated |
| :---: | :--- | :--- | :--- |
| 54 | `customer_id` | `` | Missing customer ID — row dropped |
| 55 | `invoice_date` | `NOT_A_DATE` | Unparseable date — row dropped |
| 56 | `quantity` | `-5` | Invalid quantity (≤0 or non-numeric) — row dropped |
| 57 | `unit_price` | `-2.0` | Invalid price (≤0 or non-numeric) — row dropped |

---

## 3. Behavioral Feature Engineering (RFM Table)

- **Reference Date Anchor:** `2024-10-06` (Dataset latest date + 1 day)
- **Population Median Recency:** 144.0 days
- **Population Median Frequency:** 3.0 invoices
- **Population Median Monetary:** INR 253.46

| Customer ID | Recency (days) | Frequency (orders) | Monetary Spend (INR) | R-Score (1-4) | F-Score (1-4) | M-Score (1-4) | Composite RFM |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **CUST001** | 3 | 5 | ₹253.46 | 4 | 4 | 2 | 3.20 |
| **CUST002** | 2 | 8 | ₹654.50 | 4 | 4 | 4 | 4.00 |
| **CUST003** | 413 | 3 | ₹200.00 | 1 | 2 | 2 | 1.70 |
| **CUST004** | 369 | 3 | ₹182.00 | 1 | 2 | 1 | 1.30 |
| **CUST005** | 1 | 3 | ₹52,000.00 | 4 | 2 | 4 | 3.40 |
| **CUST006** | 371 | 2 | ₹28.00 | 1 | 1 | 1 | 1.00 |
| **CUST007** | 129 | 3 | ₹282.00 | 3 | 2 | 3 | 2.70 |
| **CUST008** | 352 | 2 | ₹190.00 | 2 | 1 | 2 | 1.70 |
| **CUST009** | 169 | 3 | ₹336.00 | 2 | 2 | 3 | 2.40 |
| **CUST010** | 4 | 5 | ₹140.00 | 3 | 4 | 1 | 2.50 |
| **CUST011** | 999 | 1 | ₹5.00 | 1 | 1 | 1 | 1.00 |
| **CUST012** | 183 | 2 | ₹3,025.00 | 2 | 1 | 4 | 2.50 |
| **CUST013** | 139 | 3 | ₹217.50 | 3 | 2 | 2 | 2.30 |
| **CUST014** | 2 | 4 | ₹1,849.00 | 4 | 4 | 4 | 4.00 |
| **CUST015** | 144 | 2 | ₹325.00 | 3 | 1 | 3 | 2.40 |

---

## 4. Unsupervised K-Means Clustering & Metric Sweep

### 4.1 Hyperparameter Selection ($K = 2$ to $6$ Sweep)
| Clusters ($K$) | Silhouette Score (Higher is better) | Davies-Bouldin Index (Lower is better) | Calinski-Harabasz Index (Higher is better) | Assessment |
| :---: | :---: | :---: | :---: | :--- |
| **K = 2** | 0.4376 | 0.9209 | 10.25 | Suboptimal |
| **K = 3** | 0.4562 | 0.7150 | 13.42 | **Optimal Balance (Peak Separation)** |
| **K = 4** | 0.4291 | 0.6505 | 15.59 | Suboptimal |
| **K = 5** | 0.3879 | 0.5166 | 13.53 | Suboptimal |
| **K = 6** | 0.3870 | 0.4231 | 13.90 | Suboptimal |

### 4.2 Segment Centroids & Behavioral Cohort Profiles
| Cluster ID | Behavioral Segment Label | Size | Share (%) | Centroid Recency | Centroid Frequency | Centroid Spend | Strategic Orientation |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Cluster 0** | **Inactive Low-Value** | 2 | 13.3% | 685.0 days | 1.5 orders | ₹16.50 | Targeted Campaign |
| **Cluster 1** | **Loyal High-Value** | 3 | 20.0% | 2.0 days | 3.0 orders | ₹3,025.00 | Targeted Campaign |
| **Cluster 2** | **Recent Frequent** | 10 | 66.7% | 141.5 days | 3.0 orders | ₹235.48 | Targeted Campaign |

---

## 5. Marketing Fatigue Engine & Customer Governance Matrix

### 5.1 Audience Governance Overview
- **Total Analyzed Audience:** 15 customers
- **Approved for WhatsApp Outreach:** 12 (80.0%)
- **Blocked by Anti-Spam / Consent Rules:** 3 (20.0%)

### 5.2 Complete Policy Audit Table
| Customer ID | Behavioral Cohort | Outreach Status | Decision Rationale & Rule Triggered |
| :--- | :--- | :---: | :--- |
| **CUST014** | Loyal High-Value | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST002** | Recent Frequent | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST005** | Loyal High-Value | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST001** | Recent Frequent | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST007** | Recent Frequent | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST012** | Loyal High-Value | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST010** | Recent Frequent | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST015** | Recent Frequent | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST013** | Recent Frequent | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST004** | Recent Frequent | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST006** | Inactive Low-Value | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST011** | Inactive Low-Value | ✅ APPROVED | Passed all checks (Consent=Yes, Cap<3, Suppressed=No) |
| **CUST009** | Recent Frequent | ❌ BLOCKED | Frequency cap reached: 3 messages sent in the last 30 days (cap: 3). |
| **CUST003** | Recent Frequent | ❌ BLOCKED | No marketing consent recorded. |
| **CUST008** | Recent Frequent | ❌ BLOCKED | Customer is on the suppression/opt-out list. |

---

## 6. Explainable Campaign Recommendations & WhatsApp Message Mock

### 6.1 Sample Campaign Recommendations
#### Customer: `CUST014`
- **Cohort:** `Loyal High-Value`
- **Assigned Campaign:** `Loyalty Reward` (`loyalty_reward`)
- **Heuristic Priority Score:** `100.0` / 100
- **Explainable AI Text:** *"Customer CUST014 is classified as 'Loyal High-Value'. RFM Profile: last purchase 2 days ago, 4 distinct invoice(s), total spend £1,849.00. Recommended campaign: Loyalty Reward. Rationale: Customer has high frequency (4 invoices) and/or high monetary value. A loyalty reward reinforces retention. ✓ Eligible for campaign sending (all fatigue checks passed). Note: Engagement history is not available for this customer. Heuristic score is a ranking aid only; it does not predict response rate."*

#### Customer: `CUST002`
- **Cohort:** `Recent Frequent`
- **Assigned Campaign:** `Loyalty Reward` (`loyalty_reward`)
- **Heuristic Priority Score:** `100.0` / 100
- **Explainable AI Text:** *"Customer CUST002 is classified as 'Recent Frequent'. RFM Profile: last purchase 2 days ago, 8 distinct invoice(s), total spend £654.50. Recommended campaign: Loyalty Reward. Rationale: Customer has high frequency (8 invoices) and/or high monetary value. A loyalty reward reinforces retention. ✓ Eligible for campaign sending (all fatigue checks passed). Note: Engagement history is not available for this customer. Heuristic score is a ranking aid only; it does not predict response rate."*

#### Customer: `CUST005`
- **Cohort:** `Loyal High-Value`
- **Assigned Campaign:** `Loyalty Reward` (`loyalty_reward`)
- **Heuristic Priority Score:** `85.0` / 100
- **Explainable AI Text:** *"Customer CUST005 is classified as 'Loyal High-Value'. RFM Profile: last purchase 1 days ago, 3 distinct invoice(s), total spend £52,000.00. Recommended campaign: Loyalty Reward. Rationale: Customer has high frequency (3 invoices) and/or high monetary value. A loyalty reward reinforces retention. ✓ Eligible for campaign sending (all fatigue checks passed). Note: Engagement history is not available for this customer. Heuristic score is a ranking aid only; it does not predict response rate."*

#### Customer: `CUST001`
- **Cohort:** `Recent Frequent`
- **Assigned Campaign:** `Loyalty Reward` (`loyalty_reward`)
- **Heuristic Priority Score:** `80.0` / 100
- **Explainable AI Text:** *"Customer CUST001 is classified as 'Recent Frequent'. RFM Profile: last purchase 3 days ago, 5 distinct invoice(s), total spend £253.46. Recommended campaign: Loyalty Reward. Rationale: Customer has high frequency (5 invoices) and/or high monetary value. A loyalty reward reinforces retention. ✓ Eligible for campaign sending (all fatigue checks passed). Note: Engagement history is not available for this customer. Heuristic score is a ranking aid only; it does not predict response rate."*

### 6.2 WhatsApp Message Preview (Rendered Template)
```text
+--------------------------------------------------------------------------+
| Meta WhatsApp Cloud API [SIMULATED ADAPTER - Safe Mock Engine]           |
+--------------------------------------------------------------------------+
| Recipient: +91 98765 43210 (Masked: ***3210)                             |
| Template : loyalty_reward                                                |
| Timestamp: 2026-10-19 18:30:00 UTC                                      |
+--------------------------------------------------------------------------+
| Message Body:                                                            |
|                                                                          |
| Hello CUST002!                                                           |
| As one of our Loyal High-Value members, you have unlocked 15% OFF your   |
| next order. Use code: LOYALTY15 at checkout.                             |
|                                                                          |
| Reply STOP to opt out of future WhatsApp notifications.                  |
+--------------------------------------------------------------------------+
| Delivery Status: QUEUED_SIMULATED | Message ID: SIMULATED_A7F3B91C4E2D   |
+--------------------------------------------------------------------------+
```
