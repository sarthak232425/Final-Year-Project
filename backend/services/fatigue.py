"""
Marketing Fatigue and Eligibility Rules.

This module implements explainable, configurable business rules that determine
whether a customer is eligible to receive a marketing campaign message.

Rules (in evaluation order — first failing rule blocks the customer):

  1. CONSENT CHECK
     Customer must have consent_given=True.
     If False: blocked with reason "No marketing consent recorded."

  2. SUPPRESSION CHECK
     Customer must have suppressed=False.
     If True: blocked with reason "Customer is on the suppression/opt-out list."

  3. FREQUENCY CAP
     Customer must have received fewer than FREQUENCY_CAP messages in
     the last 30 days.
     Default cap: 3 messages per 30-day window.
     If at or above cap: blocked with reason explaining the cap and actual count.

  4. RECENCY WINDOW (configurable per segment)
     Some campaign types require a recent purchase within a configurable window.
     Example: loyalty campaigns only target customers active in the last 90 days.
     If outside window: blocked with reason.

All checks are documented and logged. The result is always accompanied by a
human-readable explanation, even when eligible.

IMPORTANT: This module checks rules only. It does NOT:
  - Predict future purchase probability (that would require an ML model).
  - Claim engagement probabilities where engagement data does not exist.
  - Use engagement data that has not been recorded in the system.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional


# ─── Configuration (configurable per campaign type) ────────────────────────

DEFAULT_FREQUENCY_CAP = 3        # Max messages per 30-day window
LOYALTY_RECENCY_DAYS = 90        # Loyalty campaigns: active within 90 days
WINBACK_MIN_RECENCY_DAYS = 60    # Win-back campaigns: inactive for at least 60 days
REENGAGEMENT_MIN_RECENCY_DAYS = 30


# ─── Output data structures ───────────────────────────────────────────────────

@dataclass
class EligibilityResult:
    customer_id: str
    eligible: bool
    blocking_reason: Optional[str]   # None if eligible
    checks_performed: list[dict]     # Full audit trail of every check


def _check(name: str, passed: bool, detail: str) -> dict:
    return {"check": name, "passed": passed, "detail": detail}


# ─── Main public function ─────────────────────────────────────────────────────

def check_eligibility(
    customer_id: str,
    consent_given: bool,
    suppressed: bool,
    messages_last_30_days: int,
    recency_days: Optional[int] = None,
    campaign_type: str = "general",
    frequency_cap: int = DEFAULT_FREQUENCY_CAP,
    today: Optional[date] = None,
) -> EligibilityResult:
    """
    Evaluate all eligibility rules for a customer and campaign type.

    Args:
        customer_id           : Customer identifier (for logging only)
        consent_given         : Whether the customer has given marketing consent
        suppressed            : Whether the customer is on the suppression list
        messages_last_30_days : Number of marketing messages sent in the last 30 days
        recency_days          : Days since last purchase (from RFM)
        campaign_type         : e.g. "general", "loyalty", "win_back", "re_engagement"
        frequency_cap         : Maximum allowed messages per 30-day window
        today                 : Reference date (defaults to date.today())

    Returns:
        EligibilityResult with eligible flag, blocking reason, and audit trail.
    """
    if today is None:
        today = date.today()

    checks: list[dict] = []
    blocking_reason: Optional[str] = None

    # ── Rule 1: Consent ─────────────────────────────────────────
    consent_check = _check(
        "consent",
        consent_given,
        "Marketing consent is recorded." if consent_given
        else "No marketing consent recorded — customer cannot be contacted."
    )
    checks.append(consent_check)
    if not consent_given:
        blocking_reason = "No marketing consent recorded."
        return EligibilityResult(customer_id, False, blocking_reason, checks)

    # ── Rule 2: Suppression ──────────────────────────────────────
    suppression_check = _check(
        "suppression",
        not suppressed,
        "Customer is not on the suppression list." if not suppressed
        else "Customer is on the suppression/opt-out list — cannot be contacted."
    )
    checks.append(suppression_check)
    if suppressed:
        blocking_reason = "Customer is on the suppression/opt-out list."
        return EligibilityResult(customer_id, False, blocking_reason, checks)

    # ── Rule 3: Frequency cap ────────────────────────────────────
    freq_passed = messages_last_30_days < frequency_cap
    freq_check = _check(
        "frequency_cap",
        freq_passed,
        f"Sent {messages_last_30_days}/{frequency_cap} messages in last 30 days — "
        + ("within cap." if freq_passed else f"cap of {frequency_cap} reached.")
    )
    checks.append(freq_check)
    if not freq_passed:
        blocking_reason = (
            f"Frequency cap reached: {messages_last_30_days} messages sent in the last "
            f"30 days (cap: {frequency_cap})."
        )
        return EligibilityResult(customer_id, False, blocking_reason, checks)

    # ── Rule 4: Campaign-type recency window ─────────────────────
    if recency_days is not None:
        if campaign_type == "loyalty":
            recency_ok = recency_days <= LOYALTY_RECENCY_DAYS
            recency_check = _check(
                "recency_window",
                recency_ok,
                f"Last purchase {recency_days} days ago "
                + (f"— within {LOYALTY_RECENCY_DAYS}-day loyalty window."
                   if recency_ok
                   else f"— outside {LOYALTY_RECENCY_DAYS}-day loyalty window.")
            )
            checks.append(recency_check)
            if not recency_ok:
                blocking_reason = (
                    f"Loyalty campaigns require a purchase within {LOYALTY_RECENCY_DAYS} days. "
                    f"Last purchase was {recency_days} days ago."
                )
                return EligibilityResult(customer_id, False, blocking_reason, checks)

        elif campaign_type == "win_back":
            recency_ok = recency_days >= WINBACK_MIN_RECENCY_DAYS
            recency_check = _check(
                "recency_window",
                recency_ok,
                f"Last purchase {recency_days} days ago "
                + (f"— qualifies for win-back (>={WINBACK_MIN_RECENCY_DAYS} days)."
                   if recency_ok
                   else f"— too recent for win-back (<{WINBACK_MIN_RECENCY_DAYS} days).")
            )
            checks.append(recency_check)
            if not recency_ok:
                blocking_reason = (
                    f"Win-back campaigns target customers inactive for at least "
                    f"{WINBACK_MIN_RECENCY_DAYS} days. Last purchase was {recency_days} days ago."
                )
                return EligibilityResult(customer_id, False, blocking_reason, checks)

    # ── All checks passed ────────────────────────────────────────
    return EligibilityResult(customer_id, True, None, checks)


def bulk_check_eligibility(
    customers: list[dict],
    campaign_type: str = "general",
    frequency_cap: int = DEFAULT_FREQUENCY_CAP,
) -> list[EligibilityResult]:
    """
    Check eligibility for a list of customer dicts.

    Each dict must contain:
        customer_id, consent_given, suppressed, messages_last_30_days
    Optional: recency_days
    """
    return [
        check_eligibility(
            customer_id=c["customer_id"],
            consent_given=c.get("consent_given", False),
            suppressed=c.get("suppressed", False),
            messages_last_30_days=c.get("messages_last_30_days", 0),
            recency_days=c.get("recency_days"),
            campaign_type=campaign_type,
            frequency_cap=frequency_cap,
        )
        for c in customers
    ]
