"""
Recommendations router.

GET  /api/v1/recommendations                    — All recommendations
GET  /api/v1/recommendations/{customer_id}      — Single customer recommendation
POST /api/v1/campaigns/preview                  — Preview campaign recipients
"""

from fastapi import APIRouter, HTTPException, status, Query
from backend.schemas.campaign import (
    RecommendationListResponseSchema,
    RecommendationSchema,
    EligibilityCheckSchema,
    CampaignPreviewRequestSchema,
    CampaignPreviewResponseSchema,
)
from backend.session import session

router = APIRouter(tags=["recommendations"])


def _rec_to_schema(r) -> RecommendationSchema:
    return RecommendationSchema(
        customer_id=r.customer_id,
        segment_label=r.segment_label,
        campaign_type=r.campaign_type,
        campaign_type_display=r.campaign_type_display,
        heuristic_score=r.heuristic_score,
        explanation=r.explanation,
        supporting_data=r.supporting_data,
        eligible=r.eligible,
        ineligibility_reason=r.ineligibility_reason,
        eligibility_checks=[
            EligibilityCheckSchema(**c) for c in r.eligibility_checks
        ],
    )


@router.get("/recommendations", response_model=RecommendationListResponseSchema)
def list_recommendations(
    eligible_only: bool = Query(False, description="Return only eligible customers"),
    segment_label: str = Query(None, description="Filter by segment label"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    """
    List campaign recommendations for all customers.

    Results are sorted: eligible customers first, then by descending heuristic score.
    Heuristic score is a rule-based ranking aid, NOT an ML prediction.
    """
    if session.recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis has been run yet. Call POST /api/v1/analysis/run first.",
        )

    recs = session.recommendations

    if eligible_only:
        recs = [r for r in recs if r.eligible]

    if segment_label:
        recs = [r for r in recs if r.segment_label == segment_label]

    eligible_count = sum(1 for r in session.recommendations if r.eligible)
    total = len(session.recommendations)

    start = (page - 1) * page_size
    end = start + page_size

    return RecommendationListResponseSchema(
        run_id=session.clustering_result.run_id if session.clustering_result else "unknown",
        total=total,
        eligible_count=eligible_count,
        ineligible_count=total - eligible_count,
        recommendations=[_rec_to_schema(r) for r in recs[start:end]],
    )


@router.get("/recommendations/{customer_id}", response_model=RecommendationSchema)
def get_customer_recommendation(customer_id: str):
    """Get the recommendation for a specific customer."""
    if session.recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis has been run yet.",
        )

    for r in session.recommendations:
        if r.customer_id == customer_id:
            return _rec_to_schema(r)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Customer '{customer_id}' not found in recommendations.",
    )


@router.post("/campaigns/preview", response_model=CampaignPreviewResponseSchema)
def preview_campaign(request: CampaignPreviewRequestSchema):
    """
    Preview which customers would receive a campaign of the given type.

    Applies eligibility checks with the requested frequency cap.
    Returns eligible and ineligible counts with explanations.
    """
    if session.recommendations is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis has been run yet.",
        )

    from backend.services.recommendations import generate_recommendations
    from backend.services.fatigue import check_eligibility, DEFAULT_FREQUENCY_CAP

    recs = session.recommendations

    # Filter by campaign type
    filtered = [r for r in recs if r.campaign_type == request.campaign_type]
    if request.segment_label:
        filtered = [r for r in filtered if r.segment_label == request.segment_label]

    # Re-check eligibility with the requested frequency cap
    from backend.services.fatigue import check_eligibility

    preview_recs = []
    for r in filtered:
        meta = next(
            (m for m in session.customer_metadata if m["customer_id"] == r.customer_id),
            {},
        )
        rfm_customer = next(
            (c for c in session.rfm_result.customers if c.customer_id == r.customer_id),
            None,
        ) if session.rfm_result else None

        eligibility = check_eligibility(
            customer_id=r.customer_id,
            consent_given=meta.get("consent_given", False),
            suppressed=meta.get("suppressed", False),
            messages_last_30_days=meta.get("messages_last_30_days", 0),
            recency_days=rfm_customer.recency_days if rfm_customer else None,
            campaign_type=request.campaign_type,
            frequency_cap=request.frequency_cap,
        )

        # Build updated recommendation with new eligibility
        from backend.services.recommendations import Recommendation as Rec, CAMPAIGN_DESCRIPTIONS, _build_explanation
        updated_rec = Rec(
            customer_id=r.customer_id,
            segment_label=r.segment_label,
            campaign_type=r.campaign_type,
            campaign_type_display=r.campaign_type_display,
            heuristic_score=r.heuristic_score,
            explanation=_build_explanation(
                customer_id=r.customer_id,
                segment_label=r.segment_label,
                campaign_type=r.campaign_type,
                recency_days=rfm_customer.recency_days if rfm_customer else 0,
                frequency=rfm_customer.frequency if rfm_customer else 0,
                monetary=rfm_customer.monetary if rfm_customer else 0.0,
                eligible=eligibility.eligible,
                ineligibility_reason=eligibility.blocking_reason,
            ),
            supporting_data=r.supporting_data,
            eligible=eligibility.eligible,
            ineligibility_reason=eligibility.blocking_reason,
            eligibility_checks=eligibility.checks_performed,
        )
        preview_recs.append(updated_rec)

    eligible_count = sum(1 for r in preview_recs if r.eligible)

    return CampaignPreviewResponseSchema(
        campaign_type=request.campaign_type,
        total_in_segment=len(preview_recs),
        eligible_count=eligible_count,
        ineligible_count=len(preview_recs) - eligible_count,
        recipients=[_rec_to_schema(r) for r in preview_recs],
    )
