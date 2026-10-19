"""
In-memory session store for the current analysis run.

For the initial review, analysis results are kept in memory between requests.
This is adequate for a single-user demo. Persistent storage (DB) is Phase 7.
"""

from __future__ import annotations
from typing import Optional
import pandas as pd
from backend.services.ingestion import CleaningSummary
from backend.services.rfm import RFMResult
from backend.services.clustering import ClusteringResult
from backend.services.recommendations import Recommendation


class AnalysisSession:
    """Holds the result of the most recent analysis run."""

    def __init__(self):
        self.raw_df: Optional[pd.DataFrame] = None
        self.cleaning_summary: Optional[CleaningSummary] = None
        self.rfm_result: Optional[RFMResult] = None
        self.clustering_result: Optional[ClusteringResult] = None
        self.recommendations: Optional[list[Recommendation]] = None
        self.customer_metadata: list[dict] = []

    def clear(self):
        self.__init__()


# Single global session for MVP
session = AnalysisSession()
