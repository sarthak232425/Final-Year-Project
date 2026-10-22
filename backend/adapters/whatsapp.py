"""
WhatsApp Business API Adapter.

Provides a clean interface separating marketing logic from message delivery.

Two implementations:
  MockWhatsAppAdapter  — Safe development adapter. Never sends real messages.
                         All results are clearly labelled SIMULATED.
                         Use this for demos and tests.

  LiveWhatsAppAdapter  — Calls the real Meta WhatsApp Business API.
                         Requires valid credentials in .env.
                         Only active when WHATSAPP_LIVE_MODE=true.
                         NEVER send real messages without verifying consent first.

The active adapter is selected by get_whatsapp_adapter() based on settings.

References:
  Meta WhatsApp Business Platform API:
  https://developers.facebook.com/docs/whatsapp/cloud-api/

IMPORTANT NOTES:
  - Phone numbers are NEVER logged in plain text (only last 4 digits max).
  - Consent and suppression must be validated BEFORE calling send_message().
  - Webhook verification follows Meta's documented HMAC-SHA256 process.
  - Message IDs are stored for idempotent duplicate webhook handling.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import httpx

from backend.config import get_settings


# ─── Shared data structures ───────────────────────────────────────────────────

@dataclass
class MessageResult:
    message_id: str
    status: str           # "queued" | "sent" | "failed"
    is_simulated: bool
    timestamp: datetime
    error: Optional[str] = None


@dataclass
class WebhookEvent:
    event_type: str       # "sent" | "delivered" | "read" | "failed"
    message_id: str
    customer_phone: str   # Masked in logs
    timestamp: datetime
    is_duplicate: bool = False
    failure_reason: Optional[str] = None



# ─── Webhook Deduplicator ───────────────────────────────────────────────────────

class WebhookDeduplicator:
    """
    Maintains an in-memory cache of observed (message_id, event_type) events
    to guarantee idempotent webhook handling and prevent duplicate side-effects.
    """
    def __init__(self, max_entries: int = 10000):
        self._max_entries = max_entries
        self._seen: dict[str, datetime] = {}

    def is_duplicate_and_record(self, message_id: str, event_type: str) -> bool:
        if not message_id:
            return False
        key = f"{message_id}:{event_type}"
        if key in self._seen:
            return True
        if len(self._seen) >= self._max_entries:
            oldest_key = next(iter(self._seen))
            del self._seen[oldest_key]
        self._seen[key] = datetime.utcnow()
        return False

    def is_duplicate(self, message_id: str, event_type: str) -> bool:
        if not message_id:
            return False
        return f"{message_id}:{event_type}" in self._seen

    def clear(self):
        self._seen.clear()


default_webhook_deduplicator = WebhookDeduplicator()


# ─── Abstract interface ────────────────────────────────────────────────────────

class WhatsAppAdapter(ABC):
    @abstractmethod
    def send_message(
        self,
        to_phone: str,
        template_name: str,
        template_params: list[str],
        language_code: str = "en_US",
    ) -> MessageResult:
        """Send a templated WhatsApp message. Returns MessageResult."""
        ...

    @abstractmethod
    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """Verify an inbound webhook is genuinely from Meta."""
        ...

    @abstractmethod
    def parse_webhook_event(self, payload: dict) -> list[WebhookEvent]:
        """Parse a webhook payload into structured events."""
        ...


# ─── Mock adapter ─────────────────────────────────────────────────────────────

class MockWhatsAppAdapter(WhatsAppAdapter):
    """
    Simulates WhatsApp message sending for development and demonstrations.

    ALL results from this adapter are labelled SIMULATED.
    No real messages are ever sent.
    """

    def __init__(self, deduplicator: Optional[WebhookDeduplicator] = None):
        self.deduplicator = deduplicator or default_webhook_deduplicator

    def send_message(
        self,
        to_phone: str,
        template_name: str,
        template_params: list[str],
        language_code: str = "en_US",
    ) -> MessageResult:
        simulated_id = f"SIMULATED_{uuid.uuid4().hex[:16].upper()}"
        masked_phone = f"***{to_phone[-4:]}" if len(to_phone) >= 4 else "****"
        print(
            f"[SIMULATED] Would send template '{template_name}' to {masked_phone}. "
            f"Message ID: {simulated_id}"
        )
        return MessageResult(
            message_id=simulated_id,
            status="queued",
            is_simulated=True,
            timestamp=datetime.utcnow(),
        )

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        # In mock mode, always returns True (no real secret to verify against)
        return True

    def parse_webhook_event(self, payload: dict) -> list[WebhookEvent]:
        """
        Parse a simulated or real webhook payload structure with deduplication.
        Returns empty list for unrecognised payloads.
        """
        events: list[WebhookEvent] = []
        try:
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    for status in value.get("statuses", []):
                        msg_id = status.get("id", "")
                        evt_type = status.get("status", "unknown")
                        is_dup = self.deduplicator.is_duplicate_and_record(msg_id, evt_type)
                        events.append(WebhookEvent(
                            event_type=evt_type,
                            message_id=msg_id,
                            customer_phone=f"***{status.get('recipient_id', '')[-4:]}",
                            timestamp=datetime.utcfromtimestamp(
                                int(status.get("timestamp", 0))
                            ),
                            is_duplicate=is_dup,
                        ))
        except Exception:
            pass
        return events


# ─── Live adapter ──────────────────────────────────────────────────────────────

class LiveWhatsAppAdapter(WhatsAppAdapter):
    """
    Calls the real Meta WhatsApp Business Cloud API.

    Requires in .env:
        WHATSAPP_TOKEN              — Bearer token from Meta Developer dashboard
        WHATSAPP_PHONE_NUMBER_ID    — Phone number ID (not the phone number itself)
        WHATSAPP_WEBHOOK_VERIFY_TOKEN
        WHATSAPP_LIVE_MODE=true

    This adapter is BLOCKED unless WHATSAPP_LIVE_MODE=true.
    """

    BASE_URL = "https://graph.facebook.com/v21.0"

    def __init__(
        self,
        settings: Optional[any] = None,
        deduplicator: Optional[WebhookDeduplicator] = None,
    ):
        cfg = settings or get_settings()
        if not cfg.whatsapp_live_mode:
            raise RuntimeError(
                "LiveWhatsAppAdapter instantiated but WHATSAPP_LIVE_MODE is false. "
                "Use MockWhatsAppAdapter for development."
            )
        if not cfg.whatsapp_token:
            raise RuntimeError("WHATSAPP_TOKEN is not set in .env.")
        if not cfg.whatsapp_phone_number_id:
            raise RuntimeError("WHATSAPP_PHONE_NUMBER_ID is not set in .env.")

        self._token = cfg.whatsapp_token
        self._phone_number_id = cfg.whatsapp_phone_number_id
        self._webhook_verify_token = cfg.whatsapp_webhook_verify_token
        self.deduplicator = deduplicator or default_webhook_deduplicator

    def send_message(
        self,
        to_phone: str,
        template_name: str,
        template_params: list[str],
        language_code: str = "en_US",
    ) -> MessageResult:
        """
        Send a WhatsApp template message via the Cloud API.
        Template must be pre-approved in Meta Business Manager.
        """
        url = f"{self.BASE_URL}/{self._phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }
        body = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": [
                    {
                        "type": "body",
                        "parameters": [
                            {"type": "text", "text": p} for p in template_params
                        ],
                    }
                ] if template_params else [],
            },
        }

        try:
            response = httpx.post(url, json=body, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            wa_id = data.get("messages", [{}])[0].get("id", "unknown")
            return MessageResult(
                message_id=wa_id,
                status="queued",
                is_simulated=False,
                timestamp=datetime.utcnow(),
            )
        except httpx.HTTPStatusError as e:
            return MessageResult(
                message_id="",
                status="failed",
                is_simulated=False,
                timestamp=datetime.utcnow(),
                error=f"HTTP {e.response.status_code}: {e.response.text[:200]}",
            )
        except Exception as e:
            return MessageResult(
                message_id="",
                status="failed",
                is_simulated=False,
                timestamp=datetime.utcnow(),
                error=str(e),
            )

    def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify Meta webhook signature using HMAC-SHA256.
        Signature format: "sha256=<hex_digest>"
        Documented at: https://developers.facebook.com/docs/messenger-platform/webhooks
        """
        if not signature.startswith("sha256="):
            return False
        expected = hmac.new(
            self._token.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        provided = signature[len("sha256="):]
        return hmac.compare_digest(expected, provided)

    def parse_webhook_event(self, payload: dict) -> list[WebhookEvent]:
        """Parse Meta webhook payload into structured events with deduplication."""
        events: list[WebhookEvent] = []
        try:
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    for status in value.get("statuses", []):
                        msg_id = status.get("id", "")
                        evt_type = status.get("status", "unknown")
                        is_dup = self.deduplicator.is_duplicate_and_record(msg_id, evt_type)
                        events.append(WebhookEvent(
                            event_type=evt_type,
                            message_id=msg_id,
                            customer_phone=f"***{status.get('recipient_id', '')[-4:]}",
                            timestamp=datetime.utcfromtimestamp(
                                int(status.get("timestamp", 0))
                            ),
                            is_duplicate=is_dup,
                            failure_reason=status.get("errors", [{}])[0].get(
                                "message"
                            ) if status.get("errors") else None,
                        ))
        except Exception:
            pass
        return events


# ─── Factory ─────────────────────────────────────────────────────────────────

def get_whatsapp_adapter() -> WhatsAppAdapter:
    """
    Return the appropriate adapter based on settings.
    MockWhatsAppAdapter is the default.
    LiveWhatsAppAdapter requires WHATSAPP_LIVE_MODE=true AND valid credentials.
    """
    settings = get_settings()
    if settings.whatsapp_live_mode and settings.whatsapp_token:
        return LiveWhatsAppAdapter()
    return MockWhatsAppAdapter()
