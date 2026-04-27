from typing import Dict, Any, Optional, List
import re

from llm.client import LLMClient
from llm.prompts import generate_prompt
from utils import extract_json_from_text, get_logger

logger = get_logger(__name__)


class IntentExtractor:

    def __init__(self):
        self.llm = LLMClient()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def extract(
        self,
        user_query: str,
        user_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        try:
            prompt = generate_prompt(user_query)
            raw_response = self.llm.call(prompt)

            print("\n================ RAW LLM RESPONSE ================\n")
            print(raw_response)
            print("\n==================================================\n")

            parsed = extract_json_from_text(raw_response)

            if not parsed:
                parsed = self._fallback_structure(user_query)

        except Exception:
            parsed = self._fallback_structure(user_query)

        # Ensure required keys exist
        parsed = self._ensure_schema(parsed)

        if user_profile:
            parsed = self._merge_user_profile(parsed, user_profile)

        parsed["soft_preferences"] = self._normalize_list(
            parsed.get("soft_preferences", [])
        )

        parsed["use_case"] = self._normalize_list(
            parsed.get("use_case", [])
        )

        return parsed

    # --------------------------------------------------
    # Schema Enforcement
    # --------------------------------------------------

    def _ensure_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:

        hard = data.get("hard_constraints", {})

        expected_keys = [
            "budget",
            "category",
            "brand",
            "weight_max_kg",
            "ram_min_gb",
            "battery_min_mah"
        ]

        for key in expected_keys:
            if key not in hard:
                hard[key] = None

        data["hard_constraints"] = hard

        if "soft_preferences" not in data:
            data["soft_preferences"] = []

        if "use_case" not in data:
            data["use_case"] = []

        return data

    # --------------------------------------------------
    # Normalize Lists
    # --------------------------------------------------

    def _normalize_list(self, items: List[str]) -> List[str]:

        normalized = []

        for item in items:
            item = str(item).strip().lower()

            item = item.replace("good", "")
            item = item.replace("best", "")
            item = item.replace("high", "")

            item = re.sub(r"\s+", " ", item).strip()

            if item:
                normalized.append(item)

        return list(set(normalized))

    # --------------------------------------------------
    # Profile Merge
    # --------------------------------------------------

    def _merge_user_profile(
        self,
        intent: Dict[str, Any],
        profile: Dict[str, Any]
    ) -> Dict[str, Any]:

        hard_constraints = intent.get("hard_constraints", {})
        soft_preferences: List[str] = intent.get("soft_preferences", [])

        budget_range = profile.get("budget_range")
        if budget_range and not hard_constraints.get("budget"):
            numbers = re.findall(r"\d+", str(budget_range))
            if numbers:
                hard_constraints["budget"] = float(max(numbers))

        for field in ["preferences", "interests"]:
            value = profile.get(field)
            if value:
                soft_preferences.extend(
                    [item.strip() for item in re.split(r"[|,]", value) if item.strip()]
                )

        intent["hard_constraints"] = hard_constraints
        intent["soft_preferences"] = list(set(soft_preferences))

        return intent

    # --------------------------------------------------
    # Fallback
    # --------------------------------------------------

    def _fallback_structure(self, query: str) -> Dict[str, Any]:

        return {
            "hard_constraints": {
                "budget": None,
                "category": None,
                "brand": None,
                "weight_max_kg": None,
                "ram_min_gb": None,
                "battery_min_mah": None
            },
            "soft_preferences": [],
            "use_case": [],
            "original_query": query
        }
