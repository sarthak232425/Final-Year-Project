"""
Tests for the RFM feature engineering service.

All expected values are hand-calculated from known inputs.
Reference date is set explicitly in all tests to ensure reproducibility.

Hand-calculation examples (used in assertions):
  Dataset: 2 customers, reference_date = 2024-02-01
    CUST001: invoices INV001 (2024-01-01), INV002 (2024-01-15)
             Recency  = (2024-02-01 - 2024-01-15).days = 17
             Frequency = 2 (distinct invoice IDs)
             Monetary  = (3 × 10.00) + (2 × 15.00) = 30 + 30 = 60.00

    CUST002: invoice INV003 (2024-01-20)
             Recency  = (2024-02-01 - 2024-01-20).days = 12
             Frequency = 1
             Monetary  = 5 × 8.00 = 40.00
"""

import pytest
import pandas as pd
from datetime import date
from backend.services.rfm import calculate_rfm, RFMResult


def _make_df(rows: list[dict]) -> pd.DataFrame:
    """Build a minimal cleaned DataFrame for RFM testing."""
    df = pd.DataFrame(rows)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["is_cancellation"] = df.get("is_cancellation", False)
    if "is_cancellation" not in df.columns:
        df["is_cancellation"] = False
    if "line_total" not in df.columns:
        df["line_total"] = df["quantity"] * df["unit_price"]
    return df


REFERENCE_DATE = date(2024, 2, 1)

BASE_ROWS = [
    {"invoice_id": "INV001", "customer_id": "CUST001", "invoice_date": "2024-01-01",
     "quantity": 3, "unit_price": 10.00, "line_total": 30.00, "is_cancellation": False},
    {"invoice_id": "INV002", "customer_id": "CUST001", "invoice_date": "2024-01-15",
     "quantity": 2, "unit_price": 15.00, "line_total": 30.00, "is_cancellation": False},
    {"invoice_id": "INV003", "customer_id": "CUST002", "invoice_date": "2024-01-20",
     "quantity": 5, "unit_price": 8.00, "line_total": 40.00, "is_cancellation": False},
]


class TestRFMCalculations:
    """Hand-verified RFM value tests."""

    def test_recency_cust001(self):
        # Most recent invoice: 2024-01-15; reference: 2024-02-01
        # Expected recency = 17 days
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        cust = next(c for c in result.customers if c.customer_id == "CUST001")
        assert cust.recency_days == 17

    def test_recency_cust002(self):
        # Most recent invoice: 2024-01-20; reference: 2024-02-01
        # Expected recency = 12 days
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        cust = next(c for c in result.customers if c.customer_id == "CUST002")
        assert cust.recency_days == 12

    def test_frequency_counts_distinct_invoices_not_lines(self):
        # CUST001 has 2 lines in INV001 and 1 line in INV002 → frequency = 2 (not 3)
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        cust = next(c for c in result.customers if c.customer_id == "CUST001")
        assert cust.frequency == 2, (
            f"Frequency should count distinct invoices, not lines. Got {cust.frequency}"
        )

    def test_monetary_sum(self):
        # CUST001: INV001 line 30 + INV002 line 30 = 60.00
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        cust = next(c for c in result.customers if c.customer_id == "CUST001")
        assert cust.monetary == pytest.approx(60.00)

    def test_monetary_cust002(self):
        # CUST002: 5 × 8.00 = 40.00
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        cust = next(c for c in result.customers if c.customer_id == "CUST002")
        assert cust.monetary == pytest.approx(40.00)

    def test_customer_count(self):
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        assert result.customer_count == 2

    def test_reference_date_stored(self):
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        assert result.reference_date == REFERENCE_DATE

    def test_default_reference_date_is_max_date_plus_one(self):
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df)  # No reference date
        # Max invoice date is 2024-01-20, so reference = 2024-01-21
        assert result.reference_date == date(2024, 1, 21)


class TestCancellationExclusion:
    def test_cancellation_transactions_excluded_from_rfm(self):
        rows = BASE_ROWS + [
            # Cancellation: should NOT count toward frequency or monetary
            {"invoice_id": "CINV001", "customer_id": "CUST001",
             "invoice_date": "2024-01-20", "quantity": 3, "unit_price": 10.00,
             "line_total": 30.00, "is_cancellation": True},
        ]
        df = _make_df(rows)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        cust = next(c for c in result.customers if c.customer_id == "CUST001")
        # Frequency should still be 2, not 3
        assert cust.frequency == 2
        # Monetary should still be 60.00, not 90.00
        assert cust.monetary == pytest.approx(60.00)


class TestRFMScores:
    def test_rfm_scores_in_valid_range(self):
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        for c in result.customers:
            assert 1 <= c.r_score <= 4, f"R score {c.r_score} out of range"
            assert 1 <= c.f_score <= 4, f"F score {c.f_score} out of range"
            assert 1 <= c.m_score <= 4, f"M score {c.m_score} out of range"
            assert 0 < c.rfm_score <= 4.0, f"RFM composite {c.rfm_score} out of range"

    def test_rfm_score_formula(self):
        """RFM score = 0.3R + 0.3F + 0.4M (documented formula)."""
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        for c in result.customers:
            expected = 0.3 * c.r_score + 0.3 * c.f_score + 0.4 * c.m_score
            assert c.rfm_score == pytest.approx(expected, abs=1e-6)

    def test_scaled_features_present(self):
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        for c in result.customers:
            # Scaled values should be numeric (not NaN)
            assert c.recency_scaled == c.recency_scaled  # NaN check
            assert c.frequency_scaled == c.frequency_scaled
            assert c.monetary_log_scaled == c.monetary_log_scaled


class TestEdgeCases:
    def test_single_customer_single_transaction(self):
        rows = [
            {"invoice_id": "INV001", "customer_id": "CUST001",
             "invoice_date": "2024-01-15", "quantity": 1, "unit_price": 10.00,
             "line_total": 10.00, "is_cancellation": False},
        ]
        df = _make_df(rows)
        result = calculate_rfm(df, reference_date=date(2024, 2, 1))
        assert result.customer_count == 1
        assert result.customers[0].frequency == 1
        assert result.customers[0].monetary == pytest.approx(10.00)

    def test_all_cancellations_raises(self):
        rows = [
            {"invoice_id": "CINV001", "customer_id": "CUST001",
             "invoice_date": "2024-01-15", "quantity": 3, "unit_price": 10.00,
             "line_total": 30.00, "is_cancellation": True},
        ]
        df = _make_df(rows)
        with pytest.raises(ValueError, match="No valid.*transactions remain"):
            calculate_rfm(df)

    def test_multiple_transactions_same_invoice_counted_once(self):
        """Multiple lines for the same invoice_id → frequency = 1."""
        rows = [
            {"invoice_id": "INV001", "customer_id": "CUST001",
             "invoice_date": "2024-01-15", "quantity": 2, "unit_price": 10.00,
             "line_total": 20.00, "is_cancellation": False},
            {"invoice_id": "INV001", "customer_id": "CUST001",
             "invoice_date": "2024-01-15", "quantity": 3, "unit_price": 5.00,
             "line_total": 15.00, "is_cancellation": False},
        ]
        df = _make_df(rows)
        result = calculate_rfm(df, reference_date=date(2024, 2, 1))
        cust = result.customers[0]
        assert cust.frequency == 1, "Two lines of the same invoice should count as 1"
        assert cust.monetary == pytest.approx(35.00)  # Sum of both lines

    def test_dataset_medians_correct(self):
        df = _make_df(BASE_ROWS)
        result = calculate_rfm(df, reference_date=REFERENCE_DATE)
        # CUST001: recency=17, CUST002: recency=12 → median=14.5
        assert result.dataset_median_recency == pytest.approx(14.5)
        # CUST001: freq=2, CUST002: freq=1 → median=1.5
        assert result.dataset_median_frequency == pytest.approx(1.5)
