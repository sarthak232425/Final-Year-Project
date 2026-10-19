"""
Data ingestion and validation service.

Accepts a CSV file as bytes, validates and cleans the data, and returns:
- A cleaned pandas DataFrame ready for RFM calculation
- A CleaningSummary describing every action taken

Expected CSV columns:
    invoice_id    : string identifier for the invoice
    customer_id   : string identifier for the customer
    invoice_date  : date/datetime string
    quantity      : integer number of units
    unit_price    : float price per unit

Optional columns (if present, validated):
    consent_given         : bool
    suppressed            : bool
    last_contact_date     : date string
    messages_last_30_days : integer

Design decisions (documented per requirement):
- Rows with missing customer_id are DROPPED; they cannot be attributed to a customer.
- Rows with missing invoice_id are DROPPED; they cannot be grouped into invoices.
- Rows with unparseable invoice_date are DROPPED.
- Rows with quantity <= 0 are DROPPED (includes returns and zero-quantity lines).
  Exception: invoices starting with 'C' are flagged as cancellations separately.
- Rows with unit_price <= 0 are DROPPED.
- Duplicate rows (same invoice_id + customer_id + quantity + unit_price) are deduplicated.
- Cancellation invoices (invoice_id starts with 'C') are retained in the DB as cancellations
  but EXCLUDED from RFM calculation.
"""

from __future__ import annotations

import io
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import pandas as pd
import numpy as np


# ─── Public data structures ───────────────────────────────────────────────────

@dataclass
class ValidationIssue:
    row_number: Optional[int]
    field: str
    value: str
    reason: str


@dataclass
class CleaningSummary:
    run_id: str
    original_row_count: int
    final_row_count: int
    cancellation_count: int
    dropped_missing_customer_id: int
    dropped_missing_invoice_id: int
    dropped_invalid_date: int
    dropped_invalid_quantity: int
    dropped_invalid_price: int
    dropped_duplicates: int
    issues: list[ValidationIssue] = field(default_factory=list)
    reference_date: Optional[str] = None  # Set after RFM calculation

    @property
    def total_dropped(self) -> int:
        return (
            self.dropped_missing_customer_id
            + self.dropped_missing_invoice_id
            + self.dropped_invalid_date
            + self.dropped_invalid_quantity
            + self.dropped_invalid_price
            + self.dropped_duplicates
        )


# ─── Required columns and their aliases ───────────────────────────────────────

REQUIRED_COLUMNS = {
    "invoice_id": ["invoice_id", "invoiceno", "invoice no", "invoice_no"],
    "customer_id": ["customer_id", "customerid", "customer id", "customer_no"],
    "invoice_date": ["invoice_date", "invoicedate", "invoice date", "date"],
    "quantity": ["quantity", "qty"],
    "unit_price": ["unit_price", "unitprice", "price", "unit price"],
}

OPTIONAL_COLUMNS = {
    "consent_given": ["consent_given", "consent"],
    "suppressed": ["suppressed", "opt_out", "optout"],
    "last_contact_date": ["last_contact_date", "last_contact"],
    "messages_last_30_days": ["messages_last_30_days", "msg_count_30d"],
}


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to canonical names by matching against known aliases."""
    rename_map: dict[str, str] = {}
    lower_cols = {c.lower().strip(): c for c in df.columns}

    for canonical, aliases in {**REQUIRED_COLUMNS, **OPTIONAL_COLUMNS}.items():
        for alias in aliases:
            if alias in lower_cols:
                rename_map[lower_cols[alias]] = canonical
                break

    return df.rename(columns=rename_map)


def _check_required_columns(df: pd.DataFrame) -> list[str]:
    """Return list of missing required column names."""
    return [col for col in REQUIRED_COLUMNS if col not in df.columns]


# ─── Main public function ─────────────────────────────────────────────────────

def ingest_csv(
    file_bytes: bytes,
    encoding: str = "utf-8",
) -> tuple[pd.DataFrame, CleaningSummary]:
    """
    Parse, validate, and clean a CSV transaction file.

    Returns:
        cleaned_df  : DataFrame with canonical columns, ready for RFM.
                      Cancellation rows are INCLUDED with is_cancellation=True
                      so they can be stored in the DB, but callers must exclude
                      them from RFM calculations.
        summary     : CleaningSummary instance describing every action taken.
    """
    run_id = str(uuid.uuid4())
    issues: list[ValidationIssue] = []

    # ── Parse CSV ─────────────────────────────────────────────────
    try:
        df = pd.read_csv(io.BytesIO(file_bytes), encoding=encoding, dtype=str, low_memory=False)
    except UnicodeDecodeError:
        # Retry with latin-1 (common for UCI dataset)
        df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin-1", dtype=str, low_memory=False)

    df = _normalise_columns(df)
    original_count = len(df)

    # ── Check required columns ────────────────────────────────────
    missing = _check_required_columns(df)
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. "
            f"Found columns: {list(df.columns)}"
        )

    # ── Strip whitespace from string columns ──────────────────────
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": pd.NA, "None": pd.NA, "": pd.NA})

    # ── Drop missing customer_id ───────────────────────────────────
    mask_missing_cid = df["customer_id"].isna()
    dropped_missing_cid = int(mask_missing_cid.sum())
    for idx in df[mask_missing_cid].index:
        issues.append(ValidationIssue(int(idx) + 2, "customer_id", "", "Missing customer ID — row dropped"))
    df = df[~mask_missing_cid].copy()

    # ── Drop missing invoice_id ────────────────────────────────────
    mask_missing_iid = df["invoice_id"].isna()
    dropped_missing_iid = int(mask_missing_iid.sum())
    for idx in df[mask_missing_iid].index:
        issues.append(ValidationIssue(int(idx) + 2, "invoice_id", "", "Missing invoice ID — row dropped"))
    df = df[~mask_missing_iid].copy()

    # ── Parse invoice_date ─────────────────────────────────────────
    parsed_dates = pd.to_datetime(df["invoice_date"], errors="coerce", format="mixed", dayfirst=True)
    mask_bad_date = parsed_dates.isna()
    dropped_bad_date = int(mask_bad_date.sum())
    for idx in df[mask_bad_date].index:
        raw_val = df.loc[idx, "invoice_date"]
        issues.append(ValidationIssue(int(idx) + 2, "invoice_date", str(raw_val), "Unparseable date — row dropped"))
    df = df[~mask_bad_date].copy()
    df["invoice_date"] = parsed_dates[~mask_bad_date].values

    # ── Flag cancellation invoices ─────────────────────────────────
    df["is_cancellation"] = [bool(str(x).startswith("C")) for x in df["invoice_id"]]
    cancellation_count = sum(1 for x in df["is_cancellation"] if x)

    # ── Parse quantity ─────────────────────────────────────────────
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    # Flag invalid: NaN or <= 0 for non-cancellation rows
    mask_bad_qty = df["quantity"].isna() | (
        (~pd.Series(df["is_cancellation"], index=df.index)) & (df["quantity"] <= 0)
    )
    dropped_bad_qty = int(mask_bad_qty.sum())
    for idx in df[mask_bad_qty].index:
        raw_val = df.loc[idx, "quantity"] if "quantity" in df.columns else ""
        issues.append(ValidationIssue(int(idx) + 2, "quantity", str(raw_val), "Invalid quantity (≤0 or non-numeric) — row dropped"))
    df = df[~mask_bad_qty].copy()
    df["quantity"] = df["quantity"].astype(int)

    # ── Parse unit_price ──────────────────────────────────────────
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    mask_bad_price = df["unit_price"].isna() | (df["unit_price"] <= 0)
    dropped_bad_price = int(mask_bad_price.sum())
    for idx in df[mask_bad_price].index:
        raw_val = df.loc[idx, "unit_price"] if "unit_price" in df.columns else ""
        issues.append(ValidationIssue(int(idx) + 2, "unit_price", str(raw_val), "Invalid price (≤0 or non-numeric) — row dropped"))
    df = df[~mask_bad_price].copy()

    # ── Compute line_total ────────────────────────────────────────
    df["line_total"] = df["quantity"] * df["unit_price"]

    # ── Deduplicate ───────────────────────────────────────────────
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["invoice_id", "customer_id", "quantity", "unit_price"])
    dropped_duplicates = before_dedup - len(df)

    # ── Optional columns — parse if present ───────────────────────
    bool_map = {"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False}
    if "consent_given" in df.columns:
        df["consent_given"] = [
            bool_map.get(str(x).strip().lower(), False) for x in df["consent_given"]
        ]
    else:
        df["consent_given"] = [False] * len(df)

    if "suppressed" in df.columns:
        df["suppressed"] = [
            bool_map.get(str(x).strip().lower(), False) for x in df["suppressed"]
        ]
    else:
        df["suppressed"] = [False] * len(df)

    if "messages_last_30_days" in df.columns:
        df["messages_last_30_days"] = pd.to_numeric(
            df["messages_last_30_days"], errors="coerce"
        ).fillna(0).astype(int)
    else:
        df["messages_last_30_days"] = 0

    df = df.reset_index(drop=True)

    summary = CleaningSummary(
        run_id=run_id,
        original_row_count=original_count,
        final_row_count=len(df),
        cancellation_count=cancellation_count,
        dropped_missing_customer_id=dropped_missing_cid,
        dropped_missing_invoice_id=dropped_missing_iid,
        dropped_invalid_date=dropped_bad_date,
        dropped_invalid_quantity=dropped_bad_qty,
        dropped_invalid_price=dropped_bad_price,
        dropped_duplicates=dropped_duplicates,
        issues=issues[:200],  # Cap reported issues to avoid huge payloads
    )

    return df, summary
