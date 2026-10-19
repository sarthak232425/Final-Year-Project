"""
Tests for the campaign recommendation engine.

Covers:
- Recommendations generated for all customers
- Ineligible customers have explanation
- Eligible customers have non-null campaign type
- Heuristic score is in valid range (0–100)
- Explanation text is present and non-empty
- Supporting data contains required fields
- Ineligible customers appear AFTER eligible ones
- Engagement marked as unavailable (not invented)
"""

import pytest
import pandas as pd
from datetime import date
from backend.services.rfm import calculate_rfm
from backend.services.clustering import cluster_customers
from backend.services.recommendations import generate_recommendations, Recommendation


def _build_full_pipeline(n_customers: int = 15):
    """Build a complete RFM + clustering result for recommendation tests."""
    import random
    random.seed(42)
    rows = []
    for i in range(n_customers):
        cid = f"CUST{i:03d}"
        for j in range(random.randint(1, 4)):
            rows.append({
                "invoice_id": f"INV{i:03d}_{j}",
                "customer_id": cid,
                "invoice_date": pd.Timestamp("2024-01-01") + pd.Timedelta(days=random.randint(0, 180)),
                "quantity": random.randint(1, 10),
                "unit_price": round(random.uniform(5.0, 100.0), 2),
                "is_cancellation": False,
            })

    df = pd.DataFrame(rows)
    df["line_total"] = df["quantity"] * df["unit_price"]
    rfm = calculate_rfm(df, reference_date=date(2024, 7, 1))
    clustering = cluster_customers(rfm, run_id="test-run", k_min=2, k_max=4, random_seed=42)

    # Mix of eligible and ineligible customers
    metadata = []
    for i, c in enumerate(rfm.customers):
        metadata.append({
            "customer_id": c.customer_id,
            "consent_given": i % 3 != 0,  # Every 3rd customer lacks consent
            "suppressed": i == 5,          # CUST005 is suppressed
            "messages_last_30_days": 4 if i == 7 else 0,  # CUST007 at cap
        })

    return rfm, clustering, metadata


class TestRecommendationGeneration:
    def test_one_recommendation_per_customer(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        assert len(recs) == rfm.customer_count

    def test_all_customers_have_campaign_type(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        for r in recs:
            assert isinstance(r.campaign_type, str)
            assert len(r.campaign_type) > 0

    def test_all_recommendations_have_explanation(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        for r in recs:
            assert isinstance(r.explanation, str)
            assert len(r.explanation) > 10, "Explanation too short"

    def test_heuristic_score_in_range(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        for r in recs:
            assert 0.0 <= r.heuristic_score <= 100.0

    def test_supporting_data_has_required_fields(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        required_fields = ["recency_days", "frequency", "monetary", "r_score",
                           "f_score", "m_score", "rfm_score", "cluster_id",
                           "consent_given", "suppressed", "messages_last_30_days"]
        for r in recs:
            for field in required_fields:
                assert field in r.supporting_data, f"Missing field: {field} in recommendation"

    def test_engagement_marked_unavailable(self):
        """Engagement data must not be invented — marked as unavailable."""
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        for r in recs:
            assert r.supporting_data.get("engagement_data") == "unavailable"
            assert "unavailable" in r.explanation.lower() or "engagement" in r.explanation.lower()


class TestEligibility:
    def test_no_consent_customer_is_ineligible(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        # Every 3rd customer lacks consent
        ineligible_recs = [r for r in recs if not r.eligible]
        assert len(ineligible_recs) > 0

    def test_ineligible_recommendation_has_reason(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        for r in recs:
            if not r.eligible:
                assert r.ineligibility_reason is not None
                assert len(r.ineligibility_reason) > 0

    def test_eligible_recommendation_no_blocking_reason(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        for r in recs:
            if r.eligible:
                assert r.ineligibility_reason is None

    def test_eligible_before_ineligible_in_list(self):
        """Eligible customers must appear before ineligible ones."""
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        found_ineligible = False
        for r in recs:
            if not r.eligible:
                found_ineligible = True
            if found_ineligible and r.eligible:
                pytest.fail("Eligible customer appeared after ineligible one in sorted list")

    def test_eligible_customers_sorted_by_descending_score(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        eligible = [r for r in recs if r.eligible]
        scores = [r.heuristic_score for r in eligible]
        assert scores == sorted(scores, reverse=True), "Eligible customers not sorted by score"


class TestExplanationContent:
    def test_explanation_mentions_segment(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        for r in recs:
            assert r.segment_label.lower() in r.explanation.lower() or \
                   any(word in r.explanation for word in r.segment_label.split()), \
                   f"Segment label not mentioned in explanation for {r.customer_id}"

    def test_ineligible_explanation_mentions_reason(self):
        rfm, clustering, metadata = _build_full_pipeline(15)
        recs = generate_recommendations(rfm, clustering, metadata)
        for r in recs:
            if not r.eligible:
                # Explanation should warn about ineligibility
                assert "not eligible" in r.explanation.lower() or \
                       "❌" in r.explanation or "⚠" in r.explanation or \
                       r.ineligibility_reason.lower()[:10] in r.explanation.lower()
