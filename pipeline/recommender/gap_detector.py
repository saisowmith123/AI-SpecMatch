from typing import List, Dict, Any
from utils import get_logger

logger = get_logger(__name__)


class GapDetector:
    """
    Detects when:
    - No product satisfies all hard constraints
    - Only partial matches exist
    - Important soft preferences are unmet

    Provides rationale and suggests closest alternatives.
    """

    def detect_gaps(
        self,
        recommendations: List[Dict[str, Any]],
        user_constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze recommendations against user constraints.
        """

        if not recommendations:
            return {
                "gap_detected": True,
                "message": "No products match the given criteria.",
                "suggestion": "Consider relaxing budget or weight constraints."
            }

        fully_matched = []
        partial_matches = []

        for rec in recommendations:
            unmet = rec.get("unmet_needs", [])
            tradeoffs = rec.get("tradeoffs", [])

            if not unmet and not tradeoffs:
                fully_matched.append(rec)
            else:
                partial_matches.append(rec)

        # Case 1: At least one perfect match
        if fully_matched:
            return {
                "gap_detected": False,
                "message": "At least one product satisfies all hard and soft constraints.",
                "perfect_matches": [r.get("product_name") for r in fully_matched]
            }

        # Case 2: Only partial matches exist
        reasons = []
        for rec in partial_matches:
            unmet = rec.get("unmet_needs", [])
            if unmet:
                reasons.extend(unmet)

        unique_reasons = list(set(reasons))

        suggestion = self._generate_suggestion(unique_reasons, user_constraints)

        return {
            "gap_detected": True,
            "message": "No product fully satisfies all criteria. Showing closest alternatives.",
            "unmet_criteria": unique_reasons,
            "suggestion": suggestion,
            "alternatives": [r.get("product_name") for r in partial_matches]
        }

    def _generate_suggestion(
        self,
        unmet_criteria: List[str],
        user_constraints: Dict[str, Any]
    ) -> str:
        """
        Generate a simple rule-based suggestion for relaxing constraints.
        """

        if not unmet_criteria:
            return "Try adjusting one or more preferences."

        suggestions = []

        for item in unmet_criteria:
            if "budget" in item.lower():
                suggestions.append("Increase budget slightly.")
            elif "weight" in item.lower():
                suggestions.append("Consider slightly heavier models.")
            elif "battery" in item.lower():
                suggestions.append("Relax battery life requirement.")
            elif "performance" in item.lower() or "ram" in item.lower():
                suggestions.append("Adjust performance expectations.")
            else:
                suggestions.append(f"Relax constraint related to '{item}'.")

        return " ".join(list(set(suggestions)))
