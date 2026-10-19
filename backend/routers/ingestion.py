"""
Data ingestion router.

POST /api/v1/ingest/upload  — Upload a CSV transaction file
GET  /api/v1/ingest/status  — Get the last ingestion summary
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.services.ingestion import ingest_csv, CleaningSummary, ValidationIssue
from backend.schemas.ingestion import (
    IngestResponseSchema,
    CleaningSummarySchema,
    ValidationIssueSchema,
)
from backend.session import session

router = APIRouter(prefix="/ingest", tags=["ingestion"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def _summary_to_schema(summary: CleaningSummary) -> CleaningSummarySchema:
    return CleaningSummarySchema(
        run_id=summary.run_id,
        original_row_count=summary.original_row_count,
        final_row_count=summary.final_row_count,
        cancellation_count=summary.cancellation_count,
        dropped_missing_customer_id=summary.dropped_missing_customer_id,
        dropped_missing_invoice_id=summary.dropped_missing_invoice_id,
        dropped_invalid_date=summary.dropped_invalid_date,
        dropped_invalid_quantity=summary.dropped_invalid_quantity,
        dropped_invalid_price=summary.dropped_invalid_price,
        dropped_duplicates=summary.dropped_duplicates,
        total_dropped=summary.total_dropped,
        issues=[
            ValidationIssueSchema(
                row_number=i.row_number,
                field=i.field,
                value=i.value,
                reason=i.reason,
            )
            for i in summary.issues
        ],
    )


@router.post("/upload", response_model=IngestResponseSchema)
async def upload_transactions(file: UploadFile = File(...)):
    """
    Upload a CSV file of transaction data.

    Required columns: invoice_id, customer_id, invoice_date, quantity, unit_price

    Returns a cleaning summary describing all rows kept, dropped, and why.
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are accepted. Please upload a .csv file.",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB.",
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    try:
        df, summary = ingest_csv(file_bytes)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {str(e)}",
        )

    if summary.final_row_count == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "No valid rows remain after cleaning. "
                "Check that your CSV has the required columns and valid data."
            ),
        )

    # Store cleaned dataframe in session for subsequent analysis
    session.clear()
    session.raw_df = df
    session.cleaning_summary = summary

    # Build customer metadata from available columns
    customer_ids = df["customer_id"].unique()
    session.customer_metadata = [
        {
            "customer_id": str(cid),
            "consent_given": bool(
                df[df["customer_id"] == cid]["consent_given"].iloc[0]
            ) if "consent_given" in df.columns else False,
            "suppressed": bool(
                df[df["customer_id"] == cid]["suppressed"].iloc[0]
            ) if "suppressed" in df.columns else False,
            "messages_last_30_days": int(
                df[df["customer_id"] == cid]["messages_last_30_days"].iloc[0]
            ) if "messages_last_30_days" in df.columns else 0,
        }
        for cid in customer_ids
    ]

    return IngestResponseSchema(
        success=True,
        message=(
            f"Successfully ingested {summary.final_row_count:,} rows "
            f"({summary.total_dropped:,} dropped, {summary.cancellation_count:,} cancellations). "
            f"Run analysis to compute RFM and segments."
        ),
        summary=_summary_to_schema(summary),
    )


@router.get("/status")
def get_ingestion_status():
    """Return the cleaning summary for the most recently uploaded file."""
    if session.cleaning_summary is None:
        return {"status": "no_data", "message": "No file has been uploaded yet."}

    return {
        "status": "ready",
        "summary": _summary_to_schema(session.cleaning_summary),
    }
