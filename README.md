# AI-Based Customer Segmentation and Personalized WhatsApp Marketing Platform

[![Project Status](https://img.shields.io/badge/Status-In%20Development-yellow)](docs/STATUS.md)
[![Review Deadline](https://img.shields.io/badge/Review-19--24%20Oct%202026-red)](docs/REVIEW_CHECKLIST.md)

> **BE Information Technology Final Year Project**  
> Second Project Review: 19–24 October 2026

---

## Overview

A business intelligence and marketing platform that:
1. Imports customer transaction data (CSV / UCI Online Retail dataset)
2. Calculates RFM (Recency, Frequency, Monetary) features per customer
3. Segments customers using K-Means clustering with interpretable labels
4. Applies explainable marketing-fatigue and consent-eligibility rules
5. Recommends personalized campaign types with transparent reasoning
6. Provides a WhatsApp integration adapter (mock mode by default; live mode requires credentials)
7. Tracks campaign events and message outcomes

---

## Quick Start (Windows — Fresh Machine)

### 1. Install Prerequisites

```powershell
# Install Python 3.11 from https://www.python.org/downloads/
# Install Node.js 20 LTS from https://nodejs.org/
# Install Git from https://git-scm.com/

# Verify installs
python --version    # should be 3.11+
node --version      # should be 20+
npm --version
git --version
```

### 2. Clone and Set Up Backend

```powershell
cd "C:\Users\Sarth\Documents\GitHub\Final-Year-Project"

# Create and activate Python virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install backend dependencies
pip install -r backend\requirements.txt

# Copy environment config
copy backend\.env.example backend\.env

# Initialize the database
python -m backend.scripts.init_db

# Start the backend API server
uvicorn backend.main:app --reload --port 8000
```

### 3. Set Up Frontend

```powershell
# In a NEW terminal window:
cd "C:\Users\Sarth\Documents\GitHub\Final-Year-Project\frontend"
npm install
npm run dev
```

### 4. Open the App

- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health

---

## Running Tests

```powershell
# Activate virtual environment first
.\venv\Scripts\Activate.ps1

# Run all backend tests
pytest backend\tests\ -v

# Run with coverage report
pytest backend\tests\ -v --cov=backend --cov-report=term-missing
```

---

## Project Structure

```
Final-Year-Project/
├── backend/                    # Python FastAPI backend
│   ├── main.py                 # Application entry point
│   ├── config.py               # Configuration and settings
│   ├── database.py             # SQLAlchemy setup
│   ├── models/                 # Database ORM models
│   ├── schemas/                # Pydantic request/response schemas
│   ├── routers/                # FastAPI route handlers
│   ├── services/               # Business logic
│   │   ├── ingestion.py        # CSV import and validation
│   │   ├── rfm.py              # RFM feature engineering
│   │   ├── clustering.py       # K-Means segmentation
│   │   ├── fatigue.py          # Marketing fatigue rules
│   │   └── recommendations.py  # Campaign recommendation engine
│   ├── adapters/               # External integrations
│   │   └── whatsapp.py         # WhatsApp Business API adapter
│   ├── tests/                  # pytest test suite
│   ├── scripts/                # Utility scripts
│   ├── data/                   # Example datasets
│   ├── requirements.txt
│   └── .env.example
├── frontend/                   # React + TypeScript + Vite frontend
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Route-level page components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── api/                # API client functions
│   │   └── types/              # TypeScript type definitions
│   ├── package.json
│   └── vite.config.ts
├── docs/                       # Project documentation
│   ├── PROJECT_PLAN.md
│   ├── STATUS.md
│   ├── ARCHITECTURE.md
│   └── REVIEW_CHECKLIST.md
└── README.md
```

---

## Dataset

The application ships with a **synthetic example dataset** (`backend/data/example_transactions.csv`) that works immediately without external downloads.

To use the **UCI Online Retail dataset** (real transaction data, no WhatsApp/consent info):
1. Download from: https://archive.ics.uci.edu/dataset/352/online-retail
2. Save as `backend/data/online_retail.xlsx`
3. Import via the dashboard upload interface

> ⚠️ The UCI dataset contains **transaction history only**. Any consent/engagement metadata shown alongside it is **synthetic and clearly labelled as such**.

---

## Team

| Role | Member | Responsibility |
|------|--------|----------------|
| Backend & Database | TBD | FastAPI, SQLAlchemy, authentication |
| Data & ML | TBD | RFM, clustering, evaluation |
| Frontend | TBD | React dashboard, visualizations |
| Integrations & QA | TBD | WhatsApp adapter, tests, deployment |

---

## Documentation

- [Project Plan](docs/PROJECT_PLAN.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Status](docs/STATUS.md)
- [Review Checklist](docs/REVIEW_CHECKLIST.md)
