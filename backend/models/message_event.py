"""MessageEvent model — records WhatsApp message delivery outcomes."""

from sqlalchemy import String, DateTime, ForeignKey, Boolean, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional
from backend.database import Base


class MessageEvent(Base):
    __tablename__ = "message_event"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(
        ForeignKey("campaign.id", ondelete="CASCADE"), nullable=False, index=True
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customer.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # WhatsApp message ID from the API response (null for simulated events)
    wa_message_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)

    # Status: queued | sent | delivered | read | failed
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="queued")

    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # TRUE for all events produced by the mock adapter.
    # Real events from the Live adapter set this to False.
    is_simulated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    campaign: Mapped["Campaign"] = relationship("Campaign", back_populates="message_events")  # noqa: F821
