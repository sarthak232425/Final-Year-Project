"""
Contextual Multi-Armed Bandit (LinUCB) Engine for Marketing Campaigns.

Balances exploration and exploitation for campaign personalization. Given a customer's
RFM context vector, the algorithm selects the campaign arm with the highest Upper
Confidence Bound (UCB), learning over time from customer conversion/engagement feedback.

Reference:
  Li, L., Chu, W., Langford, J., & Schapire, R. E. (2010).
  A contextual-bandit approach to personalized news recommendation.
  Proceedings of the 19th international conference on World Wide Web (WWW '10), 661–670.
"""

from __future__ import annotations

import numpy as np
from typing import Optional
from dataclasses import dataclass, field


DEFAULT_ARMS = [
    "loyalty_reward",
    "upsell",
    "win_back",
    "re_engagement",
]


@dataclass
class BanditRecommendation:
    arm: str
    predicted_reward: float
    confidence_bound: float
    ucb_score: float
    context_vector: list[float]
    all_arm_scores: dict[str, float] = field(default_factory=dict)


class ContextualBandit:
    """
    LinUCB (Disjoint Linear Models) Contextual Bandit algorithm.
    """

    def __init__(
        self,
        arms: Optional[list[str]] = None,
        feature_dim: int = 4,
        alpha: float = 1.0,
    ):
        """
        Args:
            arms: List of campaign arm identifiers.
            feature_dim: Dimensionality of context vector (default 4: bias, R_norm, F_norm, M_norm).
            alpha: Exploration parameter (higher = more exploration).
        """
        self.arms = arms or list(DEFAULT_ARMS)
        self.feature_dim = feature_dim
        self.alpha = alpha

        # For each arm a:
        # A[a] = D_a^T D_a + I_d (feature covariance matrix, initialized to Identity)
        # b[a] = D_a^T c_a (response vector, initialized to zeros)
        self.A: dict[str, np.ndarray] = {
            arm: np.identity(self.feature_dim, dtype=np.float64) for arm in self.arms
        }
        self.b: dict[str, np.ndarray] = {
            arm: np.zeros((self.feature_dim, 1), dtype=np.float64) for arm in self.arms
        }

    @staticmethod
    def extract_context(
        recency_days: float,
        frequency: float,
        monetary: float,
        max_recency: float = 730.0,
        max_frequency: float = 50.0,
        max_monetary: float = 50000.0,
    ) -> np.ndarray:
        """
        Normalize RFM customer features into a bounded context vector x in R^4:
        [bias, normalized_recency_freshness, normalized_frequency, normalized_log_monetary]
        """
        bias = 1.0
        # Recency freshness: 1.0 when purchase was today, approaches 0 for lapsed
        r_norm = max(0.0, min(1.0, 1.0 - (recency_days / max_recency)))
        # Frequency normalized
        f_norm = max(0.0, min(1.0, frequency / max_frequency))
        # Monetary log-scaled and normalized
        m_scaled = np.log1p(max(0.0, monetary)) / np.log1p(max_monetary)
        m_norm = float(np.clip(m_scaled, 0.0, 1.0))

        return np.array([[bias], [r_norm], [f_norm], [m_norm]], dtype=np.float64)

    def select_arm(
        self,
        context: np.ndarray,
        eligible_arms: Optional[list[str]] = None,
    ) -> BanditRecommendation:
        """
        Select best arm using LinUCB formula:
        p_{t,a} = x_t^T theta_a + alpha * sqrt(x_t^T A_a^{-1} x_t)
        """
        candidate_arms = eligible_arms or self.arms
        best_arm = candidate_arms[0]
        best_score = -float("inf")
        best_pred = 0.0
        best_cb = 0.0
        arm_scores: dict[str, float] = {}

        for arm in candidate_arms:
            A_inv = np.linalg.inv(self.A[arm])
            theta = A_inv @ self.b[arm]

            # Expected payoff
            expected_payoff = float((context.T @ theta).item())
            # Confidence interval
            variance = float((context.T @ A_inv @ context).item())
            confidence_bound = self.alpha * np.sqrt(max(0.0, variance))
            ucb = expected_payoff + confidence_bound

            arm_scores[arm] = round(ucb, 4)

            if ucb > best_score:
                best_score = ucb
                best_arm = arm
                best_pred = expected_payoff
                best_cb = confidence_bound

        return BanditRecommendation(
            arm=best_arm,
            predicted_reward=round(best_pred, 4),
            confidence_bound=round(best_cb, 4),
            ucb_score=round(best_score, 4),
            context_vector=[round(float(v.item()), 4) for v in context],
            all_arm_scores=arm_scores,
        )

    def update(self, arm: str, context: np.ndarray, reward: float):
        """
        Update the model after observing reward (e.g. 1.0 for click/purchase, 0.0 for none).
        A_a = A_a + x_t x_t^T
        b_a = b_a + r_t x_t
        """
        if arm not in self.A:
            raise ValueError(f"Unknown arm '{arm}'. Must be one of {self.arms}")

        self.A[arm] += context @ context.T
        self.b[arm] += reward * context
