"""Segment and CustomerScore models."""

from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, func, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from backend.database import Base


class Segment(Base):
    """A cluster/segment produced by one analysis run."""
    __tablename__ = "segment"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    cluster_id: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)

    # Cluster statistics
    median_recency_days: Mapped[float] = mapped_column(Float, nullable=False)
    median_frequency: Mapped[float] = mapped_column(Float, nullable=False)
    median_monetary: Mapped[float] = mapped_column(Float, nullable=False)

    # Evaluation metrics for the overall run (same for all segments in a run)
    silhouette_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    davies_bouldin_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calinski_harabasz_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    selected_k: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="segments")  # noqa: F821
    customer_scores: Mapped[list["CustomerScore"]] = relationship(
        "CustomerScore", back_populates="segment", cascade="all, delete-orphan"
    )
    campaigns: Mapped[list["Campaign"]] = relationship(  # noqa: F821
        "Campaign", back_populates="target_segment"
    )


class CustomerScore(Base):
    """RFM scores and cluster assignment for one customer in one run."""
    __tablename__ = "customer_score"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.id", ondelete="CASCADE"), nullable=False, index=True
    )
    segment_id: Mapped[int] = mapped_column(
        ForeignKey("segment.id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Raw RFM values
    recency_days: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[int] = mapped_column(Integer, nullable=False)
    monetary: Mapped[float] = mapped_column(Float, nullable=False)

    # Quartile scores 1–4
    r_score: Mapped[int] = mapped_column(Integer, nullable=False)
    f_score: Mapped[int] = mapped_column(Integer, nullable=False)
    m_score: Mapped[int] = mapped_column(Integer, nullable=False)

    # Composite RFM score (weighted sum, documented in services/rfm.py)
    rfm_score: Mapped[float] = mapped_column(Float, nullable=False)

    cluster_id: Mapped[int] = mapped_column(Integer, nullable=False)
    segment_label: Mapped[str] = mapped_column(String(100), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    customer: Mapped["Customer"] = relationship("Customer", back_populates="scores")  # noqa: F821
    segment: Mapped["Segment"] = relationship("Segment", back_populates="customer_scores")
