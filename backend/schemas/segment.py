"""Pydantic schemas for segment responses."""

from pydantic import BaseModel
from typing import Optional, List


class SegmentProfileSchema(BaseModel):
    cluster_id: int
    label: str
    size: int
    median_recency_days: float
    median_frequency: float
    median_monetary: float
    example_customer_ids: List[str]


class SegmentListResponseSchema(BaseModel):
    run_id: str
    selected_k: int
    segments: List[SegmentProfileSchema]


class CustomerSegmentSchema(BaseModel):
    customer_id: str
    cluster_id: int
    segment_label: str
    recency_days: int
    frequency: int
    monetary: float
    rfm_score: float
