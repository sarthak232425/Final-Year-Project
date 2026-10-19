"""Customer model."""

from sqlalchemy import String, Boolean, DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from backend.database import Base


class Customer(Base):
    __tablename__ = "customer"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    tenant_id: Mapped[int] = mapped_column(
        ForeignKey("tenant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # The customer identifier as it appears in the uploaded CSV
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Marketing consent and suppression
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    suppressed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_contact_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    messages_last_30_days: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Note: engagement data is SYNTHETIC when added alongside transaction-only datasets.
    # The source_is_synthetic flag indicates this.
    source_is_synthetic: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship("Tenant", back_populates="customers")  # noqa: F821
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="customer", cascade="all, delete-orphan"
    )
    scores: Mapped[list["CustomerScore"]] = relationship(  # noqa: F821
        "CustomerScore", back_populates="customer", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(  # noqa: F821
        "Recommendation", back_populates="customer", cascade="all, delete-orphan"
    )
    campaign_recipients: Mapped[list["CampaignRecipient"]] = relationship(  # noqa: F821
        "CampaignRecipient", back_populates="customer", cascade="all, delete-orphan"
    )
