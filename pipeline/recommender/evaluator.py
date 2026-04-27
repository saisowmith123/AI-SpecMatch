from typing import Dict, Any, List
from utils import get_logger

logger = get_logger(__name__)


class RecommendationEvaluator:
    """
    Evaluates:
    - Hard constraint satisfaction
    - Soft preference fulfillment
    - Trade-off transparency
    - Explainability completeness
    """

    def evaluate_single(
        self,
        recommendation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a single recommendation object.
        """

        hard_matches = recommendation.get("hard_matches", [])
        soft_matches = recommendation.get("soft_matches", [])
        tradeoffs = recommendation.get("tradeoffs", [])
        unmet = recommendation.get("unmet_needs", [])
        explanation = recommendation.get("explanation", "")

        hard_score = 1.0 if hard_matches and not unmet else 0.5 if hard_matches else 0.0
        soft_score = min(len(soft_matches) / 3, 1.0) if soft_matches else 0.0
        transparency_score = 1.0 if tradeoffs else 0.5
        explainability_score = 1.0 if explanation and len(explanation) > 30 else 0.5

        overall_score = round(
            (hard_score * 0.4) +
            (soft_score * 0.3) +
            (transparency_score * 0.15) +
            (explainability_score * 0.15),
            2
        )

        evaluation_result = {
            "hard_constraint_score": round(hard_score, 2),
            "soft_preference_score": round(soft_score, 2),
            "transparency_score": round(transparency_score, 2),
            "explainability_score": round(explainability_score, 2),
            "overall_score": overall_score
        }

        return evaluation_result

    def evaluate_batch(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate multiple recommendations and compute average score.
        """

        if not recommendations:
            return {"average_score": 0.0, "count": 0}

        scores = []
        for rec in recommendations:
            result = self.evaluate_single(rec)
            scores.append(result["overall_score"])

        average_score = round(sum(scores) / len(scores), 2)

        return {
            "average_score": average_score,
            "count": len(scores)
        }
