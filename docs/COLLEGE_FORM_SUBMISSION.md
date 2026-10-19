# Final Year Project Topic Submission Guide
**College Submission Form:** [Google Form](https://forms.gle/NkjP6Ww7BjubVnqk6)  
**Submission Deadline:** 19–24 October 2026  
**Degree / Department:** B.E. Information Technology (Final Year)

---

## Ready-to-Paste Form Responses

### 1. Finalized Project Title
```text
AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform
```

### 2. Project Domain / Area of Specialization
```text
Applied Machine Learning, Data Analytics, and Customer Relationship Management (CRM) Automation
```

### 3. Problem Statement
```text
Traditional retail marketing relies on generic, batch-and-blast promotional campaigns across email and SMS, resulting in low engagement rates (<3% click-through), high unsubscribe rates, and marketing fatigue. While WhatsApp boasts open rates exceeding 90%, brands lack intelligent, privacy-compliant mechanisms to automatically segment customers based on transactional behavior and deliver relevant, non-intrusive messages. Existing enterprise CRM solutions are either cost-prohibitive for SMEs or lack automated fatigue guardrails that prevent spam and preserve customer trust.
```

### 4. Proposed Solution & Objectives
```text
This project develops an end-to-end intelligent retention marketing platform that:
1. Ingests and cleans transactional sales data, automatically filtering cancellations and anomalous entries.
2. Formulates Recency, Frequency, and Monetary (RFM) behavioral feature vectors.
3. Performs unsupervised clustering using K-Means with automated hyperparameter selection (Silhouette Score, Davies–Bouldin Index, Calinski–Harabasz Index) to discover natural customer cohorts.
4. Generates personalized campaign recommendations paired with natural-language strategic explanations.
5. Enforces an automated fatigue prevention engine (explicit consent verification, global suppression list matching, and rolling 30-day frequency caps) prior to WhatsApp dispatch.
6. Provides an interactive web dashboard for store owners and marketers to audit segments, review recommendations, and preview simulated WhatsApp template messages.
```

### 5. Methodology & Technological Stack
```text
- Core Backend: Python 3.11, FastAPI (REST API framework), Pydantic v2 (Data validation)
- Machine Learning & Analytics: Scikit-learn (K-Means, metrics evaluation), Pandas & NumPy (RFM feature engineering)
- Storage & ORM: SQLite (relational storage with ACID compliance), SQLAlchemy v2
- Frontend Dashboard: React 18, TypeScript, Vite, Modern CSS Design System
- Messaging Gateway: Meta WhatsApp Business Cloud API architecture (abstracted adapter pattern with Mock SIMULATED engine for offline testing and live webhooks)
- Quality Assurance: Pytest test suite with hand-verified RFM calculations and edge case validation
```

### 6. Expected Outcomes & Measurable Deliverables
```text
1. A fully functioning, runnable minimum viable product (MVP) demonstrating end-to-end data ingestion, clustering, and campaign recommendation.
2. Verified clustering partition quality achieving Silhouette Score > 0.40 on transactional benchmark datasets.
3. 100% compliance with marketing fatigue rules (zero dispatches to opted-out or frequency-capped users).
4. Review-ready research paper draft analyzing unsupervised clustering dynamics and rule-guided retention marketing.
5. Standardized project documentation, architecture specifications, and viva presentation deck.
```

### 7. Hardware & Software Requirements
```text
- Hardware: Standard PC/Laptop (Intel Core i5 / AMD Ryzen 5 or higher, 8 GB RAM, 10 GB free disk space)
- Software Environment: Windows 10/11 or Linux, Python 3.11+, Node.js 20 LTS, Git
```
