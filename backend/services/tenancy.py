"""
Multi-Tenant Data Isolation & Query Enforcement Service.

Enforces strict tenant scoping across all database queries and writes to guarantee
that data from one business tenant can never leak to or be modified by another tenant.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.tenant import Tenant
from backend.models.customer import Customer
from backend.models.transaction import Transaction
from backend.models.segment import Segment
from backend.models.campaign import Campaign


class TenantIsolationError(Exception):
    """Raised when an operation attempts unauthorized cross-tenant data access."""
    pass


class TenantQueryService:
    """
    Enforces tenant_id isolation in all database read and write operations.
    """

    @staticmethod
    def create_tenant(
        db: Session,
        name: str,
    ) -> Tenant:
        tenant = Tenant(
            name=name,
        )
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant

    @staticmethod
    def get_tenant_by_id(db: Session, tenant_id: int) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        return db.scalars(stmt).first()

    @staticmethod
    def get_tenant_by_name(db: Session, name: str) -> Optional[Tenant]:
        stmt = select(Tenant).where(Tenant.name == name)
        return db.scalars(stmt).first()

    @staticmethod
    def get_customers(
        db: Session,
        tenant_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Customer]:
        """Strictly isolated customer query by tenant_id."""
        stmt = (
            select(Customer)
            .where(Customer.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
        )
        return db.scalars(stmt).all()

    @staticmethod
    def get_customer_by_external_id(
        db: Session,
        tenant_id: int,
        external_id: str,
    ) -> Optional[Customer]:
        """Strictly isolated customer lookup by tenant_id and external_id."""
        stmt = select(Customer).where(
            Customer.tenant_id == tenant_id,
            Customer.external_id == external_id,
        )
        return db.scalars(stmt).first()

    @staticmethod
    def create_customer(
        db: Session,
        tenant_id: int,
        external_id: str,
        consent_given: bool = True,
        suppressed: bool = False,
        messages_last_30_days: int = 0,
    ) -> Customer:
        """Create a new customer strictly bound to tenant_id."""
        customer = Customer(
            tenant_id=tenant_id,
            external_id=external_id,
            consent_given=consent_given,
            suppressed=suppressed,
            messages_last_30_days=messages_last_30_days,
            created_at=datetime.utcnow(),
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def get_transactions(
        db: Session,
        tenant_id: int,
        customer_id: Optional[int] = None,
    ) -> Sequence[Transaction]:
        """Strictly isolated transaction query by tenant_id."""
        stmt = select(Transaction).where(Transaction.tenant_id == tenant_id)
        if customer_id is not None:
            stmt = stmt.where(Transaction.customer_id == customer_id)
        return db.scalars(stmt).all()

    @staticmethod
    def create_transaction(
        db: Session,
        tenant_id: int,
        customer_id: int,
        invoice_id: str,
        invoice_date: datetime,
        quantity: int,
        unit_price: float,
        is_cancellation: bool = False,
    ) -> Transaction:
        """Create a new transaction strictly bound to tenant_id."""
        line_total = quantity * unit_price
        tx = Transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            invoice_id=invoice_id,
            invoice_date=invoice_date,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total,
            is_cancellation=is_cancellation,
            created_at=datetime.utcnow(),
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def get_segments(
        db: Session,
        tenant_id: int,
        run_id: Optional[str] = None,
    ) -> Sequence[Segment]:
        """Strictly isolated segment query by tenant_id."""
        stmt = select(Segment).where(Segment.tenant_id == tenant_id)
        if run_id:
            stmt = stmt.where(Segment.run_id == run_id)
        return db.scalars(stmt).all()

    @staticmethod
    def get_campaigns(
        db: Session,
        tenant_id: int,
    ) -> Sequence[Campaign]:
        """Strictly isolated campaign query by tenant_id."""
        stmt = select(Campaign).where(Campaign.tenant_id == tenant_id)
        return db.scalars(stmt).all()

    @staticmethod
    def assert_tenant_ownership(tenant_id: int, entity: any):
        """Assert that an entity belongs to the specified tenant."""
        if not hasattr(entity, "tenant_id") or entity.tenant_id != tenant_id:
            raise TenantIsolationError(
                f"Access denied: entity {type(entity).__name__} does not belong to tenant {tenant_id}"
            )
