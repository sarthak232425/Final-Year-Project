"""
Segments router.

GET /api/v1/segments              — List all segments from the last run
GET /api/v1/segments/{cluster_id} — Get customers in a specific segment
"""

from fastapi import APIRouter, HTTPException, status
from backend.schemas.segment import SegmentListResponseSchema, SegmentProfileSchema
from backend.session import session

router = APIRouter(prefix="/segments", tags=["segments"])


@router.get("", response_model=SegmentListResponseSchema)
def list_segments():
    """List all customer segments from the most recent analysis run."""
    if session.clustering_result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis has been run yet. Call POST /api/v1/analysis/run first.",
        )

    cr = session.clustering_result
    return SegmentListResponseSchema(
        run_id=cr.run_id,
        selected_k=cr.selected_k,
        segments=[
            SegmentProfileSchema(
                cluster_id=s.cluster_id,
                label=s.label,
                size=s.size,
                median_recency_days=s.median_recency_days,
                median_frequency=s.median_frequency,
                median_monetary=s.median_monetary,
                example_customer_ids=s.example_customer_ids,
            )
            for s in cr.segments
        ],
    )


@router.get("/{cluster_id}/customers")
def get_segment_customers(cluster_id: int):
    """Get customers assigned to a specific segment/cluster."""
    if session.clustering_result is None or session.rfm_result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis has been run yet.",
        )

    cr = session.clustering_result
    rfm_map = {c.customer_id: c for c in session.rfm_result.customers}

    # Validate cluster_id
    valid_ids = {s.cluster_id for s in cr.segments}
    if cluster_id not in valid_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cluster {cluster_id} not found. Valid clusters: {sorted(valid_ids)}",
        )

    customers_in_segment = [
        {
            "customer_id": cid,
            "cluster_id": clu_id,
            "segment_label": label,
            "recency_days": rfm_map[cid].recency_days if cid in rfm_map else None,
            "frequency": rfm_map[cid].frequency if cid in rfm_map else None,
            "monetary": round(rfm_map[cid].monetary, 2) if cid in rfm_map else None,
            "rfm_score": round(rfm_map[cid].rfm_score, 3) if cid in rfm_map else None,
        }
        for cid, (clu_id, label) in cr.customer_assignments.items()
        if clu_id == cluster_id
    ]

    return {
        "cluster_id": cluster_id,
        "label": next(
            (s.label for s in cr.segments if s.cluster_id == cluster_id), "Unknown"
        ),
        "customer_count": len(customers_in_segment),
        "customers": customers_in_segment,
    }
