"""
Unit tests for WhatsApp adapters and webhook deduplication.
"""

import hmac
import hashlib
import pytest
from backend.adapters.whatsapp import (
    MockWhatsAppAdapter,
    LiveWhatsAppAdapter,
    WebhookDeduplicator,
    WebhookEvent,
)


class TestWebhookDeduplicator:
    def test_first_event_is_not_duplicate(self):
        dedup = WebhookDeduplicator()
        assert dedup.is_duplicate_and_record("msg_001", "delivered") is False
        assert dedup.is_duplicate("msg_001", "delivered") is True

    def test_subsequent_identical_event_is_duplicate(self):
        dedup = WebhookDeduplicator()
        assert dedup.is_duplicate_and_record("msg_002", "read") is False
        assert dedup.is_duplicate_and_record("msg_002", "read") is True

    def test_different_event_type_for_same_message_is_not_duplicate(self):
        dedup = WebhookDeduplicator()
        assert dedup.is_duplicate_and_record("msg_003", "sent") is False
        assert dedup.is_duplicate_and_record("msg_003", "delivered") is False
        assert dedup.is_duplicate_and_record("msg_003", "read") is False

    def test_clear_resets_seen_events(self):
        dedup = WebhookDeduplicator()
        dedup.is_duplicate_and_record("msg_004", "sent")
        assert dedup.is_duplicate("msg_004", "sent") is True
        dedup.clear()
        assert dedup.is_duplicate("msg_004", "sent") is False


class TestMockAdapterDeduplication:
    def test_mock_adapter_marks_duplicate_webhooks(self):
        dedup = WebhookDeduplicator()
        adapter = MockWhatsAppAdapter(deduplicator=dedup)

        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {
                                        "id": "WAMID_999",
                                        "status": "delivered",
                                        "recipient_id": "919876543210",
                                        "timestamp": "1729574400",
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        first_events = adapter.parse_webhook_event(payload)
        assert len(first_events) == 1
        assert first_events[0].is_duplicate is False

        # Send same payload second time
        second_events = adapter.parse_webhook_event(payload)
        assert len(second_events) == 1
        assert second_events[0].is_duplicate is True


class TestLiveAdapterSafeguards:
    def test_live_adapter_blocked_when_flag_false(self, monkeypatch):
        monkeypatch.setenv("WHATSAPP_LIVE_MODE", "false")
        with pytest.raises(RuntimeError, match="WHATSAPP_LIVE_MODE is false"):
            LiveWhatsAppAdapter()

    def test_live_adapter_signature_verification(self):
        from backend.config import Settings
        token = "test_meta_webhook_secret_123"
        settings = Settings(
            whatsapp_live_mode=True,
            whatsapp_token=token,
            whatsapp_phone_number_id="1234567890",
        )

        adapter = LiveWhatsAppAdapter(settings=settings)
        payload = b'{"object": "whatsapp_business_account"}'
        expected_sig = "sha256=" + hmac.new(token.encode(), payload, hashlib.sha256).hexdigest()

        assert adapter.verify_webhook_signature(payload, expected_sig) is True
        assert adapter.verify_webhook_signature(payload, "sha256=invalidhash") is False
        assert adapter.verify_webhook_signature(payload, "badprefix") is False
