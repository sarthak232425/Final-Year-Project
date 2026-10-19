"""Campaign, CampaignRecipient, and Recommendation models."""

from sqlalchemy import String, DateTime, ForeignKey, Integer, Float, func, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from backend.database import Base


class Campaign(Base):
    __tablename__ = "campaign"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    campaign_type: Mapped[str] = mapped_column(String(100), nullable=False)
    target_segment_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("segment.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(50), default="draft", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="campaigns")  # noqa: F821
    target_segment: Mapped[Optional["Segment"]] = relationship(  # noqa: F821
        "Segment", back_populates="campaigns"
    )
    recipients: Mapped[list["CampaignRecipient"]] = relationship(
        "CampaignRecipient", back_populates="campaign", cascade="all, delete-orphan"
    )
    message_events: Mapped[list["MessageEvent"]] = relationship(  # noqa: F821
        "MessageEvent", back_populates="campaign", cascade="all, delete-orphan"
    )


class CampaignRecipient(Base):
    __tablename__ = "campaign_recipient"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.id", ondelete="CASCADE"), nullable=False, index=True
    )
    eligible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ineligibility_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendation_explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="recipients")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="campaign_recipients")  # noqa: F821


class Recommendation(Base):
    __tablename__ = "recommendation"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.id", ondelete="CASCADE"), nullable=False, index=True
    )
    run_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    campaign_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Heuristic score (0–100). NOT an ML prediction.
    # Formula documented in services/recommendations.py.
    heuristic_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Human-readable explanation of why this recommendation was made
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    # JSON-serialized dict of the data fields that drove the recommendation
    supporting_data_json: Mapped[str] = mapped_column(Text, nullable=False)

    eligible: Mapped[bool] = mapped_column(Boolean, nullable=False)
    ineligibility_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    customer: Mapped["Customer"] = relationship("Customer", back_populates="recommendations")  # noqa: F821
