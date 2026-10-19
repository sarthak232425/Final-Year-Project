"""
Tests for the marketing fatigue and eligibility rules service.

Covers:
- Consent check blocks ineligible customers
- Suppression check blocks opted-out customers
- Frequency cap enforcement
- Loyalty campaign recency window
- Win-back campaign recency window
- All checks pass for eligible customer
- Full audit trail returned
- Rules tested in isolation with explicit inputs
"""

import pytest
from backend.services.fatigue import check_eligibility, bulk_check_eligibility, EligibilityResult


class TestConsentCheck:
    def test_no_consent_blocks(self):
        result = check_eligibility(
            customer_id="CUST001",
            consent_given=False,
            suppressed=False,
            messages_last_30_days=0,
        )
        assert result.eligible is False
        assert "consent" in result.blocking_reason.lower()

    def test_consent_true_passes_first_check(self):
        result = check_eligibility(
            customer_id="CUST001",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
        )
        # Should not be blocked by consent
        assert not (not result.eligible and "consent" in (result.blocking_reason or "").lower())

    def test_audit_trail_contains_consent_check(self):
        result = check_eligibility(
            customer_id="CUST001",
            consent_given=False,
            suppressed=False,
            messages_last_30_days=0,
        )
        check_names = [c["check"] for c in result.checks_performed]
        assert "consent" in check_names

    def test_no_consent_stops_evaluation(self):
        """If consent fails, suppression check should NOT appear."""
        result = check_eligibility(
            customer_id="CUST001",
            consent_given=False,
            suppressed=True,
            messages_last_30_days=0,
        )
        check_names = [c["check"] for c in result.checks_performed]
        assert "suppression" not in check_names


class TestSuppressionCheck:
    def test_suppressed_customer_blocked(self):
        result = check_eligibility(
            customer_id="CUST002",
            consent_given=True,
            suppressed=True,
            messages_last_30_days=0,
        )
        assert result.eligible is False
        assert "suppression" in result.blocking_reason.lower() or "opt-out" in result.blocking_reason.lower()

    def test_not_suppressed_passes(self):
        result = check_eligibility(
            customer_id="CUST002",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
        )
        # Should pass suppression (may still be blocked by other rules)
        suppression_check = next(c for c in result.checks_performed if c["check"] == "suppression")
        assert suppression_check["passed"] is True


class TestFrequencyCap:
    def test_at_cap_blocked(self):
        result = check_eligibility(
            customer_id="CUST003",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=3,
            frequency_cap=3,
        )
        assert result.eligible is False
        assert "cap" in result.blocking_reason.lower() or "frequency" in result.blocking_reason.lower()

    def test_below_cap_passes(self):
        result = check_eligibility(
            customer_id="CUST003",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=2,
            frequency_cap=3,
        )
        freq_check = next(c for c in result.checks_performed if c["check"] == "frequency_cap")
        assert freq_check["passed"] is True

    def test_zero_messages_passes(self):
        result = check_eligibility(
            customer_id="CUST003",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
            frequency_cap=3,
        )
        freq_check = next(c for c in result.checks_performed if c["check"] == "frequency_cap")
        assert freq_check["passed"] is True

    def test_custom_frequency_cap(self):
        """Cap of 1 → blocked at 1 message."""
        result = check_eligibility(
            customer_id="CUST003",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=1,
            frequency_cap=1,
        )
        assert result.eligible is False

    def test_cap_detail_includes_count_and_limit(self):
        result = check_eligibility(
            customer_id="CUST003",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=4,
            frequency_cap=3,
        )
        freq_check = next(c for c in result.checks_performed if c["check"] == "frequency_cap")
        assert "4" in freq_check["detail"] or "4/3" in freq_check["detail"]


class TestLoyaltyCampaignRecency:
    def test_loyal_customer_within_window_eligible(self):
        result = check_eligibility(
            customer_id="CUST004",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
            recency_days=30,
            campaign_type="loyalty",
        )
        assert result.eligible is True

    def test_loyal_customer_outside_window_blocked(self):
        result = check_eligibility(
            customer_id="CUST004",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
            recency_days=91,  # > 90 day loyalty window
            campaign_type="loyalty",
        )
        assert result.eligible is False
        assert "loyalty" in result.blocking_reason.lower()


class TestWinBackCampaignRecency:
    def test_inactive_customer_eligible_for_winback(self):
        result = check_eligibility(
            customer_id="CUST005",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
            recency_days=90,  # >= 60 day win-back threshold
            campaign_type="win_back",
        )
        assert result.eligible is True

    def test_recent_customer_ineligible_for_winback(self):
        result = check_eligibility(
            customer_id="CUST005",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
            recency_days=30,  # < 60 day win-back threshold
            campaign_type="win_back",
        )
        assert result.eligible is False
        assert "win-back" in result.blocking_reason.lower()


class TestFullyEligibleCustomer:
    def test_all_checks_pass(self):
        result = check_eligibility(
            customer_id="CUST_OK",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=1,
            recency_days=30,
            campaign_type="general",
            frequency_cap=3,
        )
        assert result.eligible is True
        assert result.blocking_reason is None
        for c in result.checks_performed:
            assert c["passed"] is True, f"Check '{c['check']}' failed unexpectedly"


class TestBulkEligibility:
    def test_bulk_returns_one_result_per_customer(self):
        customers = [
            {"customer_id": "C1", "consent_given": True, "suppressed": False, "messages_last_30_days": 0},
            {"customer_id": "C2", "consent_given": False, "suppressed": False, "messages_last_30_days": 0},
            {"customer_id": "C3", "consent_given": True, "suppressed": True, "messages_last_30_days": 0},
        ]
        results = bulk_check_eligibility(customers)
        assert len(results) == 3
        assert results[0].eligible is True
        assert results[1].eligible is False
        assert results[2].eligible is False


class TestAuditTrail:
    def test_audit_trail_has_all_checks(self):
        result = check_eligibility(
            customer_id="CUST_OK",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
            campaign_type="general",
        )
        check_names = [c["check"] for c in result.checks_performed]
        assert "consent" in check_names
        assert "suppression" in check_names
        assert "frequency_cap" in check_names

    def test_each_check_has_required_keys(self):
        result = check_eligibility(
            customer_id="CUST_OK",
            consent_given=True,
            suppressed=False,
            messages_last_30_days=0,
        )
        for c in result.checks_performed:
            assert "check" in c
            assert "passed" in c
            assert "detail" in c
