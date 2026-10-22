"""
Unit tests for multi-tenant data isolation and query enforcement.
"""

from datetime import datetime
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.services.tenancy import TenantQueryService, TenantIsolationError
import backend.models  # Register all models


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestTenantIsolation:
    def test_tenant_creation_and_lookup(self, db_session):
        tenant = TenantQueryService.create_tenant(
            db_session,
            name="Acme Retail",
        )
        assert tenant.id is not None
        assert tenant.name == "Acme Retail"

        lookup_by_id = TenantQueryService.get_tenant_by_id(db_session, tenant.id)
        assert lookup_by_id is not None
        assert lookup_by_id.name == "Acme Retail"

        lookup_by_name = TenantQueryService.get_tenant_by_name(db_session, "Acme Retail")
        assert lookup_by_name is not None
        assert lookup_by_name.id == tenant.id

    def test_customer_isolation_between_tenants(self, db_session):
        t1 = TenantQueryService.create_tenant(db_session, "Store A")
        t2 = TenantQueryService.create_tenant(db_session, "Store B")

        # Create customers for Store A
        TenantQueryService.create_customer(db_session, tenant_id=t1.id, external_id="CUST_A1")
        TenantQueryService.create_customer(db_session, tenant_id=t1.id, external_id="CUST_A2")

        # Create customer for Store B
        TenantQueryService.create_customer(db_session, tenant_id=t2.id, external_id="CUST_B1")

        # Query Store A customers
        custs_a = TenantQueryService.get_customers(db_session, tenant_id=t1.id)
        assert len(custs_a) == 2
        external_ids_a = {c.external_id for c in custs_a}
        assert external_ids_a == {"CUST_A1", "CUST_A2"}
        assert "CUST_B1" not in external_ids_a

        # Query Store B customers
        custs_b = TenantQueryService.get_customers(db_session, tenant_id=t2.id)
        assert len(custs_b) == 1
        assert custs_b[0].external_id == "CUST_B1"

    def test_transaction_isolation_between_tenants(self, db_session):
        t1 = TenantQueryService.create_tenant(db_session, "Store A")
        t2 = TenantQueryService.create_tenant(db_session, "Store B")

        c1 = TenantQueryService.create_customer(db_session, tenant_id=t1.id, external_id="CUST_A")
        c2 = TenantQueryService.create_customer(db_session, tenant_id=t2.id, external_id="CUST_B")

        TenantQueryService.create_transaction(
            db_session,
            tenant_id=t1.id,
            customer_id=c1.id,
            invoice_id="INV-001",
            invoice_date=datetime(2024, 1, 1),
            quantity=2,
            unit_price=50.0,
        )

        TenantQueryService.create_transaction(
            db_session,
            tenant_id=t2.id,
            customer_id=c2.id,
            invoice_id="INV-002",
            invoice_date=datetime(2024, 1, 2),
            quantity=1,
            unit_price=100.0,
        )

        tx_a = TenantQueryService.get_transactions(db_session, tenant_id=t1.id)
        assert len(tx_a) == 1
        assert tx_a[0].invoice_id == "INV-001"
        assert tx_a[0].line_total == 100.0

        tx_b = TenantQueryService.get_transactions(db_session, tenant_id=t2.id)
        assert len(tx_b) == 1
        assert tx_b[0].invoice_id == "INV-002"

    def test_assert_tenant_ownership_enforcement(self, db_session):
        t1 = TenantQueryService.create_tenant(db_session, "Store A")
        t2 = TenantQueryService.create_tenant(db_session, "Store B")

        c1 = TenantQueryService.create_customer(db_session, tenant_id=t1.id, external_id="CUST_OWNED")

        # Valid ownership check passes
        TenantQueryService.assert_tenant_ownership(t1.id, c1)

        # Unauthorized access from Tenant 2 raises TenantIsolationError
        with pytest.raises(TenantIsolationError, match="Access denied"):
            TenantQueryService.assert_tenant_ownership(t2.id, c1)
