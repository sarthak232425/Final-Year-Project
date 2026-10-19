"""
Campaign Recommendation Engine.

Generates campaign type recommendations for each customer based on:
  1. Their segment label (from clustering)
  2. Their RFM values
  3. Their eligibility status (from fatigue rules)

Recommendation logic:
  Each segment maps to a preferred campaign type. The recommendation also
  includes an explanation (plain English) and the supporting data fields.

Campaign types and their segment targets:
  "win_back"       → At-Risk, Inactive Low-Value
  "loyalty_reward" → Loyal High-Value, Recent Frequent, Frequent High-Value
  "upsell"         → Recent High-Spender, High-Value Occasional
  "re_engagement"  → Low Engagement
  "general"        → Anything not matched above

Heuristic score formula (documented, NOT an ML prediction):
  score = (rfm_score / 4.0) × 100
  rfm_score is a weighted composite of R, F, M quartile scores (see rfm.py).
  This score is a ranking aid only. It does not predict future purchases,
  response rates, or campaign ROI. No training data or validation has been
  performed to calibrate this score.

If engagement data (open rates, response rates) is unavailable, the
recommendation notes this explicitly rather than inventing a value.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from typing import Optional

from backend.services.rfm import CustomerRFM, RFMResult
from backend.services.clustering import ClusteringResult
from backend.services.fatigue import EligibilityResult, check_eligibility


# ─── Segment → Campaign type mapping ─────────────────────────────────────────

SEGMENT_CAMPAIGN_MAP: dict[str, str] = {
    "Loyal High-Value": "loyalty_reward",
    "Recent High-Spender": "upsell",
    "Recent Frequent": "loyalty_reward",
    "Recent Active": "general",
    "Frequent High-Value": "loyalty_reward",
    "High-Value Occasional": "upsell",
    "Inactive Low-Value": "win_back",
    "At-Risk": "win_back",
    "Low Engagement": "re_engagement",
}

CAMPAIGN_DESCRIPTIONS: dict[str, str] = {
    "loyalty_reward": "Loyalty Reward",
    "upsell": "Upsell / Premium Offer",
    "win_back": "Win-Back Offer",
    "re_engagement": "Re-Engagement Campaign",
    "general": "General Newsletter",
}


# ─── Output data structure ────────────────────────────────────────────────────

@dataclass
class Recommendation:
    customer_id: str
    segment_label: str
    campaign_type: str
    campaign_type_display: str
    heuristic_score: float
    explanation: str
    supporting_data: dict
    eligible: bool
    ineligibility_reason: Optional[str]
    eligibility_checks: list[dict]


# ─── Explanation builders ─────────────────────────────────────────────────────

def _build_explanation(
    customer_id: str,
    segment_label: str,
    campaign_type: str,
    recency_days: int,
    frequency: int,
    monetary: float,
    eligible: bool,
    ineligibility_reason: Optional[str],
) -> str:
    display = CAMPAIGN_DESCRIPTIONS.get(campaign_type, campaign_type)

    lines = [
        f"Customer {customer_id} is classified as '{segment_label}'.",
        f"RFM Profile: last purchase {recency_days} days ago, "
        f"{frequency} distinct invoice(s), total spend £{monetary:,.2f}.",
        f"Recommended campaign: {display}.",
    ]

    if campaign_type == "win_back":
        lines.append(
            f"Rationale: Customer has been inactive for {recency_days} days with low "
            "purchase frequency. A win-back offer may prompt re-engagement."
        )
    elif campaign_type == "loyalty_reward":
        lines.append(
            f"Rationale: Customer has high frequency ({frequency} invoices) and/or "
            "high monetary value. A loyalty reward reinforces retention."
        )
    elif campaign_type == "upsell":
        lines.append(
            f"Rationale: Customer has high spend (£{monetary:,.2f}) with recent activity. "
            "An upsell or premium product offer is appropriate."
        )
    elif campaign_type == "re_engagement":
        lines.append(
            "Rationale: Customer shows low frequency and monetary value. "
            "A re-engagement message may stimulate interest."
        )
    else:
        lines.append("Rationale: General campaign suitable for this customer profile.")

    if not eligible:
        lines.append(f"⚠ NOT ELIGIBLE — {ineligibility_reason}")
    else:
        lines.append("✓ Eligible for campaign sending (all fatigue checks passed).")

    lines.append(
        "Note: Engagement history is not available for this customer. "
        "Heuristic score is a ranking aid only; it does not predict response rate."
    )

    return " ".join(lines)


# ─── Main public function ─────────────────────────────────────────────────────

def generate_recommendations(
    rfm_result: RFMResult,
    clustering_result: ClusteringResult,
    customer_metadata: list[dict],
    frequency_cap: int = 3,
) -> list[Recommendation]:
    """
    Generate a recommendation for every customer.

    Args:
        rfm_result          : Output of rfm.calculate_rfm()
        clustering_result   : Output of clustering.cluster_customers()
        customer_metadata   : List of dicts with keys:
                                customer_id, consent_given, suppressed,
                                messages_last_30_days
                              (Optional: recency_days will be filled from RFM)
        frequency_cap       : Forwarded to eligibility checks.

    Returns:
        List of Recommendation instances, one per customer.
    """
    # Build lookup maps
    rfm_map: dict[str, CustomerRFM] = {c.customer_id: c for c in rfm_result.customers}
    meta_map: dict[str, dict] = {str(m["customer_id"]): m for m in customer_metadata}

    recommendations: list[Recommendation] = []

    for customer_id, (cluster_id, label) in clustering_result.customer_assignments.items():
        rfm_data = rfm_map.get(customer_id)
        if rfm_data is None:
            continue  # Should not happen; skip defensively

        meta = meta_map.get(customer_id, {})
        campaign_type = SEGMENT_CAMPAIGN_MAP.get(label, "general")

        # Eligibility check
        eligibility = check_eligibility(
            customer_id=customer_id,
            consent_given=meta.get("consent_given", False),
            suppressed=meta.get("suppressed", False),
            messages_last_30_days=meta.get("messages_last_30_days", 0),
            recency_days=rfm_data.recency_days,
            campaign_type=campaign_type,
            frequency_cap=frequency_cap,
        )

        # Heuristic score (documented formula)
        heuristic_score = round((rfm_data.rfm_score / 4.0) * 100, 2)

        supporting_data = {
            "recency_days": rfm_data.recency_days,
            "frequency": rfm_data.frequency,
            "monetary": round(rfm_data.monetary, 2),
            "r_score": rfm_data.r_score,
            "f_score": rfm_data.f_score,
            "m_score": rfm_data.m_score,
            "rfm_score": rfm_data.rfm_score,
            "cluster_id": cluster_id,
            "consent_given": meta.get("consent_given", False),
            "suppressed": meta.get("suppressed", False),
            "messages_last_30_days": meta.get("messages_last_30_days", 0),
            "engagement_data": "unavailable",
        }

        explanation = _build_explanation(
            customer_id=customer_id,
            segment_label=label,
            campaign_type=campaign_type,
            recency_days=rfm_data.recency_days,
            frequency=rfm_data.frequency,
            monetary=rfm_data.monetary,
            eligible=eligibility.eligible,
            ineligibility_reason=eligibility.blocking_reason,
        )

        recommendations.append(Recommendation(
            customer_id=customer_id,
            segment_label=label,
            campaign_type=campaign_type,
            campaign_type_display=CAMPAIGN_DESCRIPTIONS.get(campaign_type, campaign_type),
            heuristic_score=heuristic_score,
            explanation=explanation,
            supporting_data=supporting_data,
            eligible=eligibility.eligible,
            ineligibility_reason=eligibility.blocking_reason,
            eligibility_checks=eligibility.checks_performed,
        ))

    # Sort: eligible first, then by descending heuristic score
    recommendations.sort(key=lambda r: (not r.eligible, -r.heuristic_score))
    return recommendations
