"""Pydantic schemas for data ingestion responses."""

from pydantic import BaseModel
from typing import Optional, List


class ValidationIssueSchema(BaseModel):
    row_number: Optional[int]
    field: str
    value: str
    reason: str


class CleaningSummarySchema(BaseModel):
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
    total_dropped: int
    issues: List[ValidationIssueSchema]


class IngestResponseSchema(BaseModel):
    success: bool
    message: str
    summary: CleaningSummarySchema
