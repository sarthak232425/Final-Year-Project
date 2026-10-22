"""
Unit tests for Contextual Multi-Armed Bandit (LinUCB) campaign recommendation engine.
"""

import pytest
import numpy as np
from backend.services.bandit import ContextualBandit, BanditRecommendation


class TestContextualBandit:
    def test_context_extraction_bounds(self):
        ctx = ContextualBandit.extract_context(recency_days=10, frequency=5, monetary=500.0)
        assert ctx.shape == (4, 1)
        bias, r_norm, f_norm, m_norm = ctx.flatten()
        assert bias == 1.0
        assert 0.0 <= r_norm <= 1.0
        assert 0.0 <= f_norm <= 1.0
        assert 0.0 <= m_norm <= 1.0

    def test_arm_selection_structure(self):
        bandit = ContextualBandit()
        ctx = ContextualBandit.extract_context(recency_days=2, frequency=10, monetary=2500.0)
        rec = bandit.select_arm(ctx)

        assert isinstance(rec, BanditRecommendation)
        assert rec.arm in bandit.arms
        assert rec.ucb_score >= 0.0
        assert len(rec.context_vector) == 4
        assert len(rec.all_arm_scores) == len(bandit.arms)

    def test_eligible_arms_subset_filtering(self):
        bandit = ContextualBandit()
        ctx = ContextualBandit.extract_context(recency_days=100, frequency=2, monetary=50.0)
        # Only allow win_back and re_engagement
        allowed = ["win_back", "re_engagement"]
        rec = bandit.select_arm(ctx, eligible_arms=allowed)
        assert rec.arm in allowed
        assert set(rec.all_arm_scores.keys()) == set(allowed)

    def test_learning_from_reward_feedback(self):
        bandit = ContextualBandit(alpha=0.2)
        ctx = ContextualBandit.extract_context(recency_days=1, frequency=15, monetary=5000.0)

        # Before updates, loyalty_reward and upsell have identical initialization
        rec_initial = bandit.select_arm(ctx)

        # Provide repeated positive conversions to loyalty_reward
        for _ in range(10):
            bandit.update("loyalty_reward", ctx, reward=1.0)

        # Provide non-conversions to upsell
        for _ in range(10):
            bandit.update("upsell", ctx, reward=0.0)

        rec_after = bandit.select_arm(ctx)
        assert rec_after.arm == "loyalty_reward"
        assert rec_after.all_arm_scores["loyalty_reward"] > rec_after.all_arm_scores["upsell"]
