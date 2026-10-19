"""Pydantic schemas for RFM and analysis responses."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import date


class CustomerRFMSchema(BaseModel):
    customer_id: str
    recency_days: int
    frequency: int
    monetary: float
    r_score: int
    f_score: int
    m_score: int
    rfm_score: float


class RFMResultSchema(BaseModel):
    run_id: str
    reference_date: str
    customer_count: int
    dataset_median_recency: float
    dataset_median_frequency: float
    dataset_median_monetary: float
    customers: List[CustomerRFMSchema]


class KValueMetricSchema(BaseModel):
    k: int
    silhouette: Optional[float]


class ClusteringMetricsSchema(BaseModel):
    run_id: str
    selected_k: int
    silhouette_score: Optional[float]
    davies_bouldin_index: Optional[float]
    calinski_harabasz_score: Optional[float]
    k_evaluation: List[KValueMetricSchema]
    random_seed: int


class AnalysisRunResponseSchema(BaseModel):
    success: bool
    run_id: str
    message: str
    rfm: RFMResultSchema
    metrics: ClusteringMetricsSchema
