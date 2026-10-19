"""
RFM Feature Engineering Service.

Calculates Recency, Frequency, and Monetary values at the customer level.

Definitions (documented):
  Recency  : Number of days between the customer's most recent invoice date
             and the reference date. Lower = more recent = better.
  Frequency: Count of distinct invoice_id values per customer.
             Counts invoices, not transaction lines.
  Monetary : Sum of (quantity × unit_price) for valid (non-cancellation) lines.

Reference date:
  Set to one day after the latest invoice_date in the cleaned dataset.
  This is the most common convention for RFM analysis and avoids a recency
  of zero for the most recent customer.

Preprocessing before clustering:
  - Monetary is log-transformed (log1p) to reduce right-skew.
  - All three features are scaled with RobustScaler (robust to outliers).

Quartile scoring (1–4):
  Each of R, F, M is binned into quartiles.
  For Recency: lower days = higher score (reversed).
  For Frequency and Monetary: higher value = higher score.

Composite RFM score:
  rfm_score = (0.3 × R_score) + (0.3 × F_score) + (0.4 × M_score)
  Weights are configurable and documented here, not opaque.
  This is a heuristic ranking aid, NOT an ML prediction.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

import numpy as np
import pandas as pd


# ─── Output data structure ────────────────────────────────────────────────────

@dataclass
class CustomerRFM:
    customer_id: str
    recency_days: int
    frequency: int
    monetary: float
    r_score: int   # 1–4 quartile
    f_score: int   # 1–4 quartile
    m_score: int   # 1–4 quartile
    rfm_score: float

    # Scaled values used as clustering inputs
    recency_scaled: float
    frequency_scaled: float
    monetary_log_scaled: float


@dataclass
class RFMResult:
    reference_date: date
    customer_count: int
    customers: list[CustomerRFM]
    dataset_median_recency: float
    dataset_median_frequency: float
    dataset_median_monetary: float


# ─── Scoring helpers ──────────────────────────────────────────────────────────

def _quartile_score(series: pd.Series, ascending: bool = True) -> pd.Series:
    """
    Assign quartile score 1–4.
    If ascending=True: higher value → higher score.
    If ascending=False (Recency): lower value → higher score.
    Handles ties and small datasets (fewer than 4 unique values).
    """
    try:
        if ascending:
            return pd.qcut(series, q=4, labels=[1, 2, 3, 4], duplicates="drop").astype(float).fillna(2)
        else:
            return pd.qcut(series, q=4, labels=[4, 3, 2, 1], duplicates="drop").astype(float).fillna(2)
    except ValueError:
        # Fewer unique values than quartiles — rank instead
        if ascending:
            return series.rank(method="min", ascending=True).apply(
                lambda x: min(4, max(1, int(np.ceil(x / len(series) * 4))))
            )
        else:
            return series.rank(method="min", ascending=False).apply(
                lambda x: min(4, max(1, int(np.ceil(x / len(series) * 4))))
            )


# ─── Main public function ─────────────────────────────────────────────────────

def calculate_rfm(
    df: pd.DataFrame,
    reference_date: Optional[date] = None,
) -> RFMResult:
    """
    Calculate RFM features from a cleaned transaction DataFrame.

    Args:
        df             : Output of ingestion.ingest_csv(). Must contain
                         invoice_id, customer_id, invoice_date, quantity,
                         unit_price, line_total, is_cancellation columns.
        reference_date : The cutoff date for recency calculation.
                         Defaults to max(invoice_date) + 1 day.

    Returns:
        RFMResult with per-customer RFM values and dataset-level statistics.
    """
    # Exclude cancellation transactions from RFM
    valid = df[~df["is_cancellation"]].copy()

    if len(valid) == 0:
        raise ValueError("No valid (non-cancellation) transactions remain after cleaning.")

    # Ensure invoice_date is datetime
    if not pd.api.types.is_datetime64_any_dtype(valid["invoice_date"]):
        valid["invoice_date"] = pd.to_datetime(valid["invoice_date"])

    # Determine reference date
    max_date = valid["invoice_date"].max().date()
    if reference_date is None:
        reference_date = max_date + timedelta(days=1)

    ref_ts = pd.Timestamp(reference_date)

    # ── Aggregate per customer ────────────────────────────────────
    rfm = valid.groupby("customer_id").agg(
        last_purchase=("invoice_date", "max"),
        frequency=("invoice_id", "nunique"),   # distinct invoices
        monetary=("line_total", "sum"),
    ).reset_index()

    rfm["recency_days"] = (ref_ts - rfm["last_purchase"]).dt.days.astype(int)

    # ── Quartile scores ───────────────────────────────────────────
    rfm["r_score"] = _quartile_score(rfm["recency_days"], ascending=False).astype(int)
    rfm["f_score"] = _quartile_score(rfm["frequency"], ascending=True).astype(int)
    rfm["m_score"] = _quartile_score(rfm["monetary"], ascending=True).astype(int)

    # Composite score (heuristic, documented weights)
    rfm["rfm_score"] = (
        0.3 * rfm["r_score"] +
        0.3 * rfm["f_score"] +
        0.4 * rfm["m_score"]
    )

    # ── Scaled features for clustering ───────────────────────────
    from sklearn.preprocessing import RobustScaler

    monetary_log = np.log1p(rfm["monetary"].values)

    cluster_matrix = np.column_stack([
        rfm["recency_days"].values,
        rfm["frequency"].values,
        monetary_log,
    ])

    scaler = RobustScaler()
    scaled = scaler.fit_transform(cluster_matrix)

    rfm["recency_scaled"] = scaled[:, 0]
    rfm["frequency_scaled"] = scaled[:, 1]
    rfm["monetary_log_scaled"] = scaled[:, 2]

    # ── Build result ───────────────────────────────────────────────
    customers = [
        CustomerRFM(
            customer_id=str(row.customer_id),
            recency_days=int(row.recency_days),
            frequency=int(row.frequency),
            monetary=float(row.monetary),
            r_score=int(row.r_score),
            f_score=int(row.f_score),
            m_score=int(row.m_score),
            rfm_score=float(row.rfm_score),
            recency_scaled=float(row.recency_scaled),
            frequency_scaled=float(row.frequency_scaled),
            monetary_log_scaled=float(row.monetary_log_scaled),
        )
        for row in rfm.itertuples()
    ]

    return RFMResult(
        reference_date=reference_date,
        customer_count=len(customers),
        customers=customers,
        dataset_median_recency=float(rfm["recency_days"].median()),
        dataset_median_frequency=float(rfm["frequency"].median()),
        dataset_median_monetary=float(rfm["monetary"].median()),
    )
