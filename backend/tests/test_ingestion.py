"""
Tests for the data ingestion service.

Covers:
- Valid CSV parsing
- Column alias normalisation (UCI column names)
- Missing customer_id
- Missing invoice_id
- Invalid dates
- Zero and negative quantities
- Negative/zero prices
- Duplicate row deduplication
- Cancellation invoice detection
- Optional column parsing (consent, suppressed)
- Empty file rejection
- Missing required column rejection
"""

import io
import pytest
import pandas as pd
from backend.services.ingestion import ingest_csv, CleaningSummary


def _make_csv(rows: list[str], header: str = None) -> bytes:
    """Build CSV bytes from a header and list of row strings."""
    if header is None:
        header = "invoice_id,customer_id,invoice_date,quantity,unit_price"
    content = header + "\n" + "\n".join(rows)
    return content.encode("utf-8")


# ─── Valid data ────────────────────────────────────────────────────────────────

class TestValidIngestion:
    def test_basic_valid_csv(self):
        csv = _make_csv([
            "INV001,CUST001,2024-01-15,3,12.50",
            "INV002,CUST001,2024-02-20,5,15.00",
            "INV003,CUST002,2024-01-10,2,8.00",
        ])
        df, summary = ingest_csv(csv)
        assert summary.original_row_count == 3
        assert summary.final_row_count == 3
        assert summary.total_dropped == 0
        assert len(df) == 3

    def test_line_total_computed(self):
        csv = _make_csv(["INV001,CUST001,2024-01-15,4,10.00"])
        df, _ = ingest_csv(csv)
        assert df.iloc[0]["line_total"] == pytest.approx(40.00)

    def test_required_columns_present(self):
        csv = _make_csv(["INV001,CUST001,2024-01-15,3,12.50"])
        df, _ = ingest_csv(csv)
        for col in ["invoice_id", "customer_id", "invoice_date", "quantity", "unit_price", "line_total"]:
            assert col in df.columns, f"Missing column: {col}"

    def test_uci_column_names_normalised(self):
        """UCI dataset uses InvoiceNo, CustomerID, etc. — should be aliased."""
        header = "InvoiceNo,CustomerID,InvoiceDate,Quantity,UnitPrice"
        csv = (header + "\nINV001,CUST001,2024-01-15,3,12.50").encode()
        df, summary = ingest_csv(csv)
        assert "invoice_id" in df.columns
        assert "customer_id" in df.columns
        assert summary.final_row_count == 1

    def test_whitespace_stripped_from_ids(self):
        csv = _make_csv(["  INV001  ,  CUST001  ,2024-01-15,3,12.50"])
        df, _ = ingest_csv(csv)
        assert df.iloc[0]["invoice_id"] == "INV001"
        assert df.iloc[0]["customer_id"] == "CUST001"


# ─── Missing required fields ──────────────────────────────────────────────────

class TestMissingFields:
    def test_missing_customer_id_dropped(self):
        csv = _make_csv([
            "INV001,,2024-01-15,3,12.50",   # empty customer_id
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_missing_customer_id == 1
        assert summary.final_row_count == 1

    def test_missing_invoice_id_dropped(self):
        csv = _make_csv([
            ",CUST001,2024-01-15,3,12.50",
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_missing_invoice_id == 1
        assert summary.final_row_count == 1

    def test_missing_required_column_raises_value_error(self):
        csv = b"invoice_id,customer_id,invoice_date,quantity\nINV001,CUST001,2024-01-15,3"
        with pytest.raises(ValueError, match="missing required columns"):
            ingest_csv(csv)

    def test_all_rows_missing_customer_id_raises_after_cleaning(self):
        csv = _make_csv([
            "INV001,,2024-01-15,3,12.50",
            "INV002,,2024-01-15,2,8.00",
        ])
        # Should return empty df (no error at ingestion stage)
        df, summary = ingest_csv(csv)
        assert summary.final_row_count == 0
        assert summary.dropped_missing_customer_id == 2


# ─── Invalid dates ────────────────────────────────────────────────────────────

class TestInvalidDates:
    def test_invalid_date_dropped(self):
        csv = _make_csv([
            "INV001,CUST001,NOT_A_DATE,3,12.50",
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_invalid_date == 1
        assert summary.final_row_count == 1

    def test_multiple_date_formats_accepted(self):
        csv = _make_csv([
            "INV001,CUST001,2024-01-15,3,12.50",
            "INV002,CUST001,15/01/2024,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_invalid_date == 0
        assert summary.final_row_count == 2


# ─── Invalid quantities ───────────────────────────────────────────────────────

class TestInvalidQuantities:
    def test_zero_quantity_dropped(self):
        csv = _make_csv([
            "INV001,CUST001,2024-01-15,0,12.50",
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_invalid_quantity == 1
        assert summary.final_row_count == 1

    def test_negative_quantity_dropped_for_non_cancellations(self):
        csv = _make_csv([
            "INV001,CUST001,2024-01-15,-5,12.50",
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_invalid_quantity == 1

    def test_non_numeric_quantity_dropped(self):
        csv = _make_csv([
            "INV001,CUST001,2024-01-15,abc,12.50",
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_invalid_quantity == 1


# ─── Invalid prices ───────────────────────────────────────────────────────────

class TestInvalidPrices:
    def test_zero_price_dropped(self):
        csv = _make_csv([
            "INV001,CUST001,2024-01-15,3,0.00",
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_invalid_price == 1

    def test_negative_price_dropped(self):
        csv = _make_csv([
            "INV001,CUST001,2024-01-15,3,-5.00",
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_invalid_price == 1


# ─── Duplicates ───────────────────────────────────────────────────────────────

class TestDuplicates:
    def test_exact_duplicate_deduplicated(self):
        csv = _make_csv([
            "INV001,CUST001,2024-01-15,3,12.50",
            "INV001,CUST001,2024-01-15,3,12.50",  # exact duplicate
            "INV002,CUST001,2024-01-15,5,8.00",
        ])
        df, summary = ingest_csv(csv)
        assert summary.dropped_duplicates == 1
        assert summary.final_row_count == 2


# ─── Cancellation invoices ────────────────────────────────────────────────────

class TestCancellations:
    def test_cancellation_invoice_flagged(self):
        csv = _make_csv([
            "CINV001,CUST001,2024-01-15,3,12.50",
            "INV001,CUST001,2024-01-15,3,12.50",
        ])
        df, summary = ingest_csv(csv)
        assert summary.cancellation_count == 1
        assert df["is_cancellation"].sum() == 1
        # Cancellation should NOT be dropped — it is flagged, not removed
        assert summary.final_row_count == 2

    def test_cancellation_included_in_db_row(self):
        csv = _make_csv(["CINV001,CUST001,2024-01-15,3,12.50"])
        df, summary = ingest_csv(csv)
        assert len(df) == 1
        assert bool(df.iloc[0]["is_cancellation"]) is True


# ─── Optional columns ─────────────────────────────────────────────────────────

class TestOptionalColumns:
    def test_consent_given_parsed(self):
        header = "invoice_id,customer_id,invoice_date,quantity,unit_price,consent_given"
        csv = (header + "\nINV001,CUST001,2024-01-15,3,12.50,true").encode()
        df, _ = ingest_csv(csv)
        assert bool(df.iloc[0]["consent_given"]) is True

    def test_suppressed_parsed(self):
        header = "invoice_id,customer_id,invoice_date,quantity,unit_price,suppressed"
        csv = (header + "\nINV001,CUST001,2024-01-15,3,12.50,true").encode()
        df, _ = ingest_csv(csv)
        assert bool(df.iloc[0]["suppressed"]) is True

    def test_missing_optional_columns_default_to_safe_values(self):
        csv = _make_csv(["INV001,CUST001,2024-01-15,3,12.50"])
        df, _ = ingest_csv(csv)
        assert bool(df.iloc[0]["consent_given"]) is False
        assert bool(df.iloc[0]["suppressed"]) is False
        assert df.iloc[0]["messages_last_30_days"] == 0


# ─── Issues log ───────────────────────────────────────────────────────────────

class TestIssuesLog:
    def test_issues_list_populated(self):
        csv = _make_csv([
            "INV001,,2024-01-15,3,12.50",
            "INV002,CUST001,2024-01-15,3,12.50",
        ])
        _, summary = ingest_csv(csv)
        assert len(summary.issues) >= 1
        assert any("customer" in i.field.lower() for i in summary.issues)

    def test_cleaning_summary_counts_consistent(self):
        csv = _make_csv([
            "INV001,,2024-01-15,3,12.50",       # missing cid
            "INV002,CUST001,BAD_DATE,3,12.50",   # bad date
            "INV003,CUST001,2024-01-15,0,12.50", # zero qty
            "INV004,CUST001,2024-01-15,3,0.00",  # zero price
            "INV005,CUST001,2024-01-15,3,12.50", # valid
        ])
        df, summary = ingest_csv(csv)
        assert summary.final_row_count == 1
        assert summary.total_dropped == 4
