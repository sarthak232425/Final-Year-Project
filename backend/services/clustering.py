"""
Customer Clustering Service.

Applies K-Means clustering to scaled RFM features and evaluates quality.

Algorithm: K-Means (scikit-learn KMeans)
  - Uses scaled [recency, frequency, log(monetary)] features
  - Tries K from k_min to k_max (default 2–10)
  - Selects K with the highest Silhouette Score
  - Falls back to k_min if only one K is feasible

Evaluation metrics:
  - Silhouette Score       : Range [-1, 1]. Higher is better.
                             Measures how similar a point is to its own cluster
                             vs. other clusters.
  - Davies–Bouldin Index   : Range [0, ∞). Lower is better.
                             Measures average similarity between each cluster
                             and its most similar cluster.
  - Calinski–Harabasz Score: Range [0, ∞). Higher is better.
                             Ratio of between-cluster to within-cluster dispersion.

Reproducibility:
  - Fixed random_state=42 by default (configurable via settings).

Segment label generation:
  Labels are assigned dynamically based on each cluster's median RFM values
  relative to the dataset median. Labels are NOT hardcoded to cluster numbers.

  Logic:
    If median_recency low AND median_frequency high AND median_monetary high:
        → "Loyal High-Value"
    If median_recency low AND median_monetary high:
        → "Recent High-Spender"
    If median_recency low:
        → "Recent Active"
    If median_frequency high AND median_monetary high:
        → "Frequent High-Value"
    If median_recency high AND median_frequency low AND median_monetary low:
        → "Inactive Low-Value"
    If median_recency high AND median_frequency low:
        → "At-Risk"
    If median_monetary high:
        → "High-Value Occasional"
    Else:
        → "Low Engagement"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
)

from backend.services.rfm import CustomerRFM, RFMResult


# ─── Output data structures ───────────────────────────────────────────────────

@dataclass
class SegmentProfile:
    cluster_id: int
    label: str
    size: int
    median_recency_days: float
    median_frequency: float
    median_monetary: float
    example_customer_ids: list[str]  # Anonymised: up to 3 external IDs


@dataclass
class ClusteringResult:
    run_id: str
    selected_k: int
    silhouette_score: Optional[float]
    davies_bouldin_index: Optional[float]
    calinski_harabasz_score: Optional[float]
    segments: list[SegmentProfile]
    # Map: customer_id → (cluster_id, label)
    customer_assignments: dict[str, tuple[int, str]]
    # All K values tried with their silhouette scores
    k_evaluation: list[dict]
    random_seed: int


# ─── Label generation ─────────────────────────────────────────────────────────

def _assign_label(
    median_recency: float,
    median_frequency: float,
    median_monetary: float,
    dataset_median_recency: float,
    dataset_median_frequency: float,
    dataset_median_monetary: float,
) -> str:
    """
    Dynamically assign a descriptive label based on cluster medians vs.
    dataset medians. Returns a human-readable segment name.
    """
    low_recency = median_recency <= dataset_median_recency
    high_frequency = median_frequency >= dataset_median_frequency
    high_monetary = median_monetary >= dataset_median_monetary

    if low_recency and high_frequency and high_monetary:
        return "Loyal High-Value"
    elif low_recency and high_monetary:
        return "Recent High-Spender"
    elif low_recency and high_frequency:
        return "Recent Frequent"
    elif low_recency:
        return "Recent Active"
    elif high_frequency and high_monetary:
        return "Frequent High-Value"
    elif high_monetary:
        return "High-Value Occasional"
    elif not low_recency and not high_frequency and not high_monetary:
        return "Inactive Low-Value"
    elif not low_recency and not high_frequency:
        return "At-Risk"
    else:
        return "Low Engagement"


# ─── Main public function ─────────────────────────────────────────────────────

def cluster_customers(
    rfm_result: RFMResult,
    run_id: str,
    k_min: int = 2,
    k_max: int = 10,
    random_seed: int = 42,
) -> ClusteringResult:
    """
    Cluster customers using K-Means on scaled RFM features.

    Handles edge cases:
    - Fewer customers than k_min → raises ValueError with clear message.
    - Fewer customers than k_max → caps k_max at n_customers - 1.
    - Only one feasible K → uses it without silhouette comparison.

    Args:
        rfm_result  : Output of rfm.calculate_rfm()
        run_id      : Unique identifier for this analysis run
        k_min, k_max: Range of K values to evaluate
        random_seed : Fixed for reproducibility

    Returns:
        ClusteringResult with metrics, segment profiles, and customer assignments.
    """
    customers = rfm_result.customers
    n = len(customers)

    if n < 2:
        raise ValueError(
            f"Cannot cluster {n} customer(s). Need at least 2. "
            "Import more transaction data."
        )

    # Cap k_max to n (KMeans allows up to n_clusters == n_samples)
    effective_k_max = min(k_max, n)
    effective_k_min = min(k_min, effective_k_max)

    # Build feature matrix
    X = np.array([
        [c.recency_scaled, c.frequency_scaled, c.monetary_log_scaled]
        for c in customers
    ])

    # ── Evaluate K range ──────────────────────────────────────────
    k_evaluation: list[dict] = []
    best_k = effective_k_min
    best_silhouette = -2.0

    for k in range(effective_k_min, effective_k_max + 1):
        km = KMeans(n_clusters=k, random_state=random_seed, n_init="auto")
        labels = km.fit_predict(X)

        # Silhouette requires at least 2 clusters with >1 member each
        n_unique_labels = len(set(labels))
        if n_unique_labels < 2:
            sil = None
        else:
            try:
                sil = float(silhouette_score(X, labels))
            except Exception:
                sil = None

        k_evaluation.append({"k": k, "silhouette": sil})

        if sil is not None and sil > best_silhouette:
            best_silhouette = sil
            best_k = k

    # ── Final clustering with selected K ─────────────────────────
    km_final = KMeans(n_clusters=best_k, random_state=random_seed, n_init="auto")
    final_labels = km_final.fit_predict(X)

    # ── Compute final metrics ─────────────────────────────────────
    n_unique = len(set(final_labels))
    if 1 < n_unique < len(X):
        try:
            sil_final = float(silhouette_score(X, final_labels))
        except Exception:
            sil_final = None
        try:
            db_final = float(davies_bouldin_score(X, final_labels))
        except Exception:
            db_final = None
        try:
            ch_final = float(calinski_harabasz_score(X, final_labels))
        except Exception:
            ch_final = None
    else:
        sil_final = None
        db_final = None
        ch_final = None

    # ── Build segment profiles ────────────────────────────────────
    import pandas as pd

    df = pd.DataFrame({
        "customer_id": [c.customer_id for c in customers],
        "recency_days": [c.recency_days for c in customers],
        "frequency": [c.frequency for c in customers],
        "monetary": [c.monetary for c in customers],
        "cluster_id": final_labels,
    })

    segments: list[SegmentProfile] = []
    customer_assignments: dict[str, tuple[int, str]] = {}

    for cluster_id in sorted(df["cluster_id"].unique()):
        cluster_df = df[df["cluster_id"] == cluster_id]

        med_r = float(cluster_df["recency_days"].median())
        med_f = float(cluster_df["frequency"].median())
        med_m = float(cluster_df["monetary"].median())

        label = _assign_label(
            med_r, med_f, med_m,
            rfm_result.dataset_median_recency,
            rfm_result.dataset_median_frequency,
            rfm_result.dataset_median_monetary,
        )

        example_ids = cluster_df["customer_id"].head(3).tolist()

        segments.append(SegmentProfile(
            cluster_id=int(cluster_id),
            label=label,
            size=len(cluster_df),
            median_recency_days=med_r,
            median_frequency=med_f,
            median_monetary=med_m,
            example_customer_ids=example_ids,
        ))

        for cid in cluster_df["customer_id"]:
            customer_assignments[str(cid)] = (int(cluster_id), label)

    return ClusteringResult(
        run_id=run_id,
        selected_k=best_k,
        silhouette_score=sil_final,
        davies_bouldin_index=db_final,
        calinski_harabasz_score=ch_final,
        segments=segments,
        customer_assignments=customer_assignments,
        k_evaluation=k_evaluation,
        random_seed=random_seed,
    )
