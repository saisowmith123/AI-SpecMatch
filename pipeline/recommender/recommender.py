import pandas as pd
from typing import Dict, Any, List, Optional

from pipeline.recommender.intent_extractor import IntentExtractor
from pipeline.recommender.matcher import Matcher
from pipeline.recommender.enricher import Enricher
from pipeline.recommender.gap_detector import GapDetector
from pipeline.recommender.evaluator import RecommendationEvaluator

from config import (
    TOP_K_RESULTS,
    ENABLE_ENRICHMENT,
    USER_PROFILE_PATH
)
from utils import get_logger

logger = get_logger(__name__)


class Recommender:
    """
    Full SpecSense AI pipeline aligned with intended architecture.

    Flow:
    1. Load user profile
    2. Extract structured intent
    3. Structured + semantic matching
    4. Enrichment
    5. Transparency layer
    6. Gap detection
    7. Evaluation scoring
    """

    def __init__(self):
        self.intent_extractor = IntentExtractor()
        self.matcher = Matcher()
        self.enricher = Enricher()
        self.gap_detector = GapDetector()
        self.evaluator = RecommendationEvaluator()

        self.user_df = self._load_user_profiles()

        logger.info("SpecSense Recommender initialized.")

    # --------------------------------------------------
    # Load User Profiles
    # --------------------------------------------------

    def _load_user_profiles(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(USER_PROFILE_PATH)
            logger.info(f"Loaded {len(df)} user profiles.")
            return df
        except Exception as e:
            logger.error(f"Failed to load user profiles: {e}")
            return pd.DataFrame()

    #def _get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
    def _get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:

        if self.user_df.empty:
            return None

        #user_row = self.user_df[self.user_df["user_id"] == user_id]
        user_row = self.user_df[
                    self.user_df["ser_id"].astype(str) == str(user_id)
                ]    
        #user_row = self.user_df[self.user_df["ser_id"] == user_id]
               
        if user_row.empty:
            return None

        return user_row.iloc[0].to_dict()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def recommend(
        self,
        user_query: str,
        #user_id: Optional[int] = None
        user_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:

        logger.info("Starting recommendation pipeline.")

        # 1️⃣ Fetch profile
        user_profile = None
        if user_id is not None:
            user_profile = self._get_user_profile(user_id)

        # 2️⃣ Extract intent
        intent = self.intent_extractor.extract(
            user_query=user_query,
            user_profile=user_profile
        )

        # 3️⃣ Match
        matched_products = self.matcher.match(
            intent=intent,
            top_k=TOP_K_RESULTS
        )

        if not matched_products:
            logger.warning("No products matched hard constraints.")

        # 4️⃣ Enrichment
        if ENABLE_ENRICHMENT:
            matched_products = self.enricher.enrich_batch(matched_products)

        # 5️⃣ Transparency Layer
        for product in matched_products:
            product["explanation"] = self._generate_explanation(
                product,
                intent
            )

        # 6️⃣ Gap Detection
        gap_info = self.gap_detector.detect_gaps(
            recommendations=matched_products,
            user_constraints=intent.get("hard_constraints", {})
        )

        for product in matched_products:
            product["gap_analysis"] = gap_info

        # 7️⃣ Evaluation
        for product in matched_products:
            evaluation = self.evaluator.evaluate_single(product)
            product["evaluation"] = evaluation

        logger.info("Recommendation pipeline completed.")

        return matched_products

    # --------------------------------------------------
    # Explanation Generator
    # --------------------------------------------------

    def _generate_explanation(
        self,
        product: Dict[str, Any],
        intent: Dict[str, Any]
    ) -> str:

        hard = product.get("hard_matches", [])
        soft = product.get("soft_matches", [])
        tradeoffs = product.get("tradeoffs", [])
        use_case = intent.get("use_case", [])

        explanation_parts = []

        if hard:
            explanation_parts.append(
                f"Meets hard constraints: {', '.join(hard)}."
            )

        if use_case:
            explanation_parts.append(
                f"Aligned for use-case: {', '.join(use_case)}."
            )

        if soft:
            explanation_parts.append(
                f"Satisfies soft preferences: {', '.join(soft)}."
            )

        if tradeoffs:
            explanation_parts.append(
                f"Trade-offs: {', '.join(tradeoffs)}."
            )

        if not explanation_parts:
            explanation_parts.append(
                "This product partially matches your request."
            )

        return " ".join(explanation_parts)
