"""
Tests for K-Means clustering service.

Covers:
- Basic clustering runs without error
- Metrics are computed and in valid ranges
- Segment labels are generated dynamically
- Small datasets are handled gracefully
- Edge case: fewer customers than k_min
- Reproducibility with fixed random seed
- customer_assignments covers all customers
"""

import pytest
import pandas as pd
from datetime import date
from backend.services.rfm import calculate_rfm
from backend.services.clustering import cluster_customers, ClusteringResult


def _make_rfm_result(n_customers: int = 10):
    """Build a minimal RFM result for clustering tests."""
    import random
    random.seed(42)
    rows = []
    for i in range(n_customers):
        cid = f"CUST{i:03d}"
        for j in range(random.randint(1, 5)):
            rows.append({
                "invoice_id": f"INV{i:03d}_{j}",
                "customer_id": cid,
                "invoice_date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=random.randint(0, 180)),
                "quantity": random.randint(1, 10),
                "unit_price": round(random.uniform(5.0, 100.0), 2),
                "is_cancellation": False,
            })

    df = pd.DataFrame(rows)
    df["line_total"] = df["quantity"] * df["unit_price"]
    return calculate_rfm(df, reference_date=date(2024, 7, 1))


class TestClustering:
    def test_basic_clustering_runs(self):
        rfm = _make_rfm_result(15)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=5, random_seed=42)
        assert isinstance(result, ClusteringResult)
        assert result.selected_k >= 2

    def test_silhouette_score_in_valid_range(self):
        rfm = _make_rfm_result(20)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=5, random_seed=42)
        if result.silhouette_score is not None:
            assert -1.0 <= result.silhouette_score <= 1.0

    def test_davies_bouldin_non_negative(self):
        rfm = _make_rfm_result(20)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=5, random_seed=42)
        if result.davies_bouldin_index is not None:
            assert result.davies_bouldin_index >= 0.0

    def test_calinski_harabasz_non_negative(self):
        rfm = _make_rfm_result(20)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=5, random_seed=42)
        if result.calinski_harabasz_score is not None:
            assert result.calinski_harabasz_score >= 0.0

    def test_all_customers_assigned(self):
        rfm = _make_rfm_result(15)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=4, random_seed=42)
        assert len(result.customer_assignments) == rfm.customer_count
        for cust in rfm.customers:
            assert cust.customer_id in result.customer_assignments

    def test_segment_count_matches_selected_k(self):
        rfm = _make_rfm_result(20)
        result = cluster_customers(rfm, run_id="test-run", k_min=3, k_max=5, random_seed=42)
        assert len(result.segments) == result.selected_k

    def test_segment_sizes_sum_to_customer_count(self):
        rfm = _make_rfm_result(20)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=4, random_seed=42)
        total = sum(s.size for s in result.segments)
        assert total == rfm.customer_count

    def test_segment_labels_are_non_empty_strings(self):
        rfm = _make_rfm_result(15)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=4, random_seed=42)
        for seg in result.segments:
            assert isinstance(seg.label, str)
            assert len(seg.label) > 0

    def test_reproducibility(self):
        """Same input + same seed must produce same cluster assignment."""
        rfm = _make_rfm_result(20)
        result1 = cluster_customers(rfm, run_id="run1", k_min=2, k_max=5, random_seed=42)
        result2 = cluster_customers(rfm, run_id="run2", k_min=2, k_max=5, random_seed=42)
        assert result1.selected_k == result2.selected_k
        for cid in result1.customer_assignments:
            assert result1.customer_assignments[cid][0] == result2.customer_assignments[cid][0]

    def test_k_evaluation_list_populated(self):
        rfm = _make_rfm_result(15)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=4, random_seed=42)
        assert len(result.k_evaluation) == 3  # k=2,3,4

    def test_random_seed_stored(self):
        rfm = _make_rfm_result(10)
        result = cluster_customers(rfm, run_id="test-run", random_seed=99)
        assert result.random_seed == 99


class TestSmallDatasets:
    def test_two_customers_minimum(self):
        """Two customers is the minimum viable input."""
        rows = [
            {"invoice_id": "INV001", "customer_id": "CUST001",
             "invoice_date": pd.Timestamp("2024-01-01"), "quantity": 1,
             "unit_price": 10.0, "line_total": 10.0, "is_cancellation": False},
            {"invoice_id": "INV002", "customer_id": "CUST002",
             "invoice_date": pd.Timestamp("2024-01-15"), "quantity": 2,
             "unit_price": 20.0, "line_total": 40.0, "is_cancellation": False},
        ]
        df = pd.DataFrame(rows)
        rfm = calculate_rfm(df, reference_date=date(2024, 2, 1))
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=5, random_seed=42)
        assert result.selected_k == 2  # Only 2 customers → k capped at 1, so min=2
        assert len(result.segments) <= 2

    def test_one_customer_raises(self):
        rows = [
            {"invoice_id": "INV001", "customer_id": "CUST001",
             "invoice_date": pd.Timestamp("2024-01-01"), "quantity": 1,
             "unit_price": 10.0, "line_total": 10.0, "is_cancellation": False},
        ]
        df = pd.DataFrame(rows)
        rfm = calculate_rfm(df, reference_date=date(2024, 2, 1))
        with pytest.raises(ValueError, match="Cannot cluster"):
            cluster_customers(rfm, run_id="test-run")

    def test_k_max_capped_at_n_minus_1(self):
        """5 customers → k_max effectively capped at 4."""
        rfm = _make_rfm_result(5)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=10, random_seed=42)
        assert result.selected_k <= 4  # n-1 = 4


class TestSegmentLabels:
    def test_labels_are_from_known_set(self):
        """Labels should be one of the documented options."""
        known_labels = {
            "Loyal High-Value", "Recent High-Spender", "Recent Frequent",
            "Recent Active", "Frequent High-Value", "High-Value Occasional",
            "Inactive Low-Value", "At-Risk", "Low Engagement"
        }
        rfm = _make_rfm_result(30)
        result = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=6, random_seed=42)
        for seg in result.segments:
            assert seg.label in known_labels, f"Unexpected label: {seg.label}"
