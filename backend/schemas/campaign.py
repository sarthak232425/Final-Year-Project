"""Pydantic schemas for recommendation responses."""

from pydantic import BaseModel
from typing import Optional, List, Any, Dict


class EligibilityCheckSchema(BaseModel):
    check: str
    passed: bool
    detail: str


class RecommendationSchema(BaseModel):
    customer_id: str
    segment_label: str
    campaign_type: str
    campaign_type_display: str
    heuristic_score: float
    explanation: str
    supporting_data: Dict[str, Any]
    eligible: bool
    ineligibility_reason: Optional[str]
    eligibility_checks: List[EligibilityCheckSchema]


class RecommendationListResponseSchema(BaseModel):
    run_id: str
    total: int
    eligible_count: int
    ineligible_count: int
    recommendations: List[RecommendationSchema]


class CampaignPreviewRequestSchema(BaseModel):
    campaign_type: str
    segment_label: Optional[str] = None
    frequency_cap: int = 3


class CampaignPreviewResponseSchema(BaseModel):
    campaign_type: str
    total_in_segment: int
    eligible_count: int
    ineligible_count: int
    recipients: List[RecommendationSchema]
