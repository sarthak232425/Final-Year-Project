"""
Analysis router — runs RFM + clustering on ingested data.

POST /api/v1/analysis/run     — Run full analysis pipeline
GET  /api/v1/analysis/rfm     — Get RFM results
GET  /api/v1/analysis/metrics — Get clustering evaluation metrics
"""

from fastapi import APIRouter, HTTPException, status, Query
from backend.services.rfm import calculate_rfm
from backend.services.clustering import cluster_customers
from backend.services.recommendations import generate_recommendations
from backend.schemas.rfm import (
    AnalysisRunResponseSchema,
    RFMResultSchema,
    CustomerRFMSchema,
    ClusteringMetricsSchema,
    KValueMetricSchema,
)
from backend.session import session
from backend.config import get_settings

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/run", response_model=AnalysisRunResponseSchema)
def run_analysis():
    """
    Run the full analysis pipeline on the currently ingested data:
      1. Calculate RFM features per customer
      2. K-Means clustering with K selection (Silhouette)
      3. Generate campaign recommendations

    Requires: A CSV file must have been uploaded first via POST /ingest/upload
    """
    if session.raw_df is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data available. Upload a CSV file first via POST /api/v1/ingest/upload",
        )

    settings = get_settings()

    # Step 1: RFM
    try:
        rfm_result = calculate_rfm(session.raw_df)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    run_id = session.cleaning_summary.run_id if session.cleaning_summary else "unknown"

    # Step 2: Clustering
    try:
        clustering_result = cluster_customers(
            rfm_result=rfm_result,
            run_id=run_id,
            k_min=settings.clustering_k_min,
            k_max=settings.clustering_k_max,
            random_seed=settings.clustering_random_seed,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    # Step 3: Recommendations
    recommendations = generate_recommendations(
        rfm_result=rfm_result,
        clustering_result=clustering_result,
        customer_metadata=session.customer_metadata,
    )

    # Store results in session
    session.rfm_result = rfm_result
    session.clustering_result = clustering_result
    session.recommendations = recommendations

    # Build response
    rfm_schema = RFMResultSchema(
        run_id=run_id,
        reference_date=str(rfm_result.reference_date),
        customer_count=rfm_result.customer_count,
        dataset_median_recency=rfm_result.dataset_median_recency,
        dataset_median_frequency=rfm_result.dataset_median_frequency,
        dataset_median_monetary=rfm_result.dataset_median_monetary,
        customers=[
            CustomerRFMSchema(
                customer_id=c.customer_id,
                recency_days=c.recency_days,
                frequency=c.frequency,
                monetary=c.monetary,
                r_score=c.r_score,
                f_score=c.f_score,
                m_score=c.m_score,
                rfm_score=c.rfm_score,
            )
            for c in rfm_result.customers[:100]  # Cap at 100 for response size
        ],
    )

    metrics_schema = ClusteringMetricsSchema(
        run_id=run_id,
        selected_k=clustering_result.selected_k,
        silhouette_score=clustering_result.silhouette_score,
        davies_bouldin_index=clustering_result.davies_bouldin_index,
        calinski_harabasz_score=clustering_result.calinski_harabasz_score,
        k_evaluation=[KValueMetricSchema(**kv) for kv in clustering_result.k_evaluation],
        random_seed=clustering_result.random_seed,
    )

    return AnalysisRunResponseSchema(
        success=True,
        run_id=run_id,
        message=(
            f"Analysis complete. {rfm_result.customer_count} customers segmented into "
            f"{clustering_result.selected_k} clusters. "
            f"Silhouette Score: "
            f"{clustering_result.silhouette_score:.4f}"
            if clustering_result.silhouette_score is not None
            else f"Analysis complete. {rfm_result.customer_count} customers segmented."
        ),
        rfm=rfm_schema,
        metrics=metrics_schema,
    )


@router.get("/rfm")
def get_rfm(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
):
    """Get paginated RFM results for all customers."""
    if session.rfm_result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis has been run yet. Call POST /api/v1/analysis/run first.",
        )

    r = session.rfm_result
    customers = r.customers
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "run_id": session.clustering_result.run_id if session.clustering_result else "unknown",
        "reference_date": str(r.reference_date),
        "customer_count": r.customer_count,
        "dataset_median_recency": r.dataset_median_recency,
        "dataset_median_frequency": r.dataset_median_frequency,
        "dataset_median_monetary": r.dataset_median_monetary,
        "page": page,
        "page_size": page_size,
        "total_pages": (r.customer_count + page_size - 1) // page_size,
        "customers": [
            {
                "customer_id": c.customer_id,
                "recency_days": c.recency_days,
                "frequency": c.frequency,
                "monetary": round(c.monetary, 2),
                "r_score": c.r_score,
                "f_score": c.f_score,
                "m_score": c.m_score,
                "rfm_score": round(c.rfm_score, 3),
            }
            for c in customers[start:end]
        ],
    }


@router.get("/metrics")
def get_metrics():
    """Get clustering evaluation metrics for the most recent analysis run."""
    if session.clustering_result is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No analysis has been run yet. Call POST /api/v1/analysis/run first.",
        )

    cr = session.clustering_result
    return {
        "run_id": cr.run_id,
        "selected_k": cr.selected_k,
        "silhouette_score": cr.silhouette_score,
        "davies_bouldin_index": cr.davies_bouldin_index,
        "calinski_harabasz_score": cr.calinski_harabasz_score,
        "k_evaluation": cr.k_evaluation,
        "random_seed": cr.random_seed,
        "note": (
            "Silhouette Score: range [-1, 1], higher is better. "
            "Davies-Bouldin Index: lower is better. "
            "Calinski-Harabasz Score: higher is better."
        ),
    }
