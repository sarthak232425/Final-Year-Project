"""ORM models package. Import all models here so SQLAlchemy registers them."""

from backend.models.tenant import Tenant
from backend.models.customer import Customer
from backend.models.transaction import Transaction
from backend.models.segment import Segment, CustomerScore
from backend.models.campaign import Campaign, CampaignRecipient, Recommendation
from backend.models.message_event import MessageEvent

__all__ = [
    "Tenant",
    "Customer",
    "Transaction",
    "Segment",
    "CustomerScore",
    "Campaign",
    "CampaignRecipient",
    "Recommendation",
    "MessageEvent",
]
