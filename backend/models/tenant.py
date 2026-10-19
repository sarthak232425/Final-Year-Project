"""Tenant model — represents a business using the platform."""

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from backend.database import Base


class Tenant(Base):
    __tablename__ = "tenant"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    customers: Mapped[list["Customer"]] = relationship(  # noqa: F821
        "Customer", back_populates="tenant", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(  # noqa: F821
        "Transaction", back_populates="tenant", cascade="all, delete-orphan"
    )
    segments: Mapped[list["Segment"]] = relationship(  # noqa: F821
        "Segment", back_populates="tenant", cascade="all, delete-orphan"
    )
    campaigns: Mapped[list["Campaign"]] = relationship(  # noqa: F821
        "Campaign", back_populates="tenant", cascade="all, delete-orphan"
    )
