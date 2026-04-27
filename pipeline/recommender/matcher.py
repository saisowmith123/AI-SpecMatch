import pandas as pd
from typing import Dict, Any, List, Tuple
import re

from config import PRODUCT_CATALOG_PATH
from utils import get_logger

logger = get_logger(__name__)


class Matcher:

    def __init__(self, catalog_path: str | None = None):
        self.catalog_path = catalog_path or PRODUCT_CATALOG_PATH
        self.catalog_df = self._load_catalog()

    # --------------------------------------------------
    # Load Catalog
    # --------------------------------------------------

    def _load_catalog(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.catalog_path)
            df["price"] = pd.to_numeric(df["price"], errors="coerce")
            logger.info(f"Loaded catalog with {len(df)} products.")
            return df
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            return pd.DataFrame()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def match(self, intent: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:

        if self.catalog_df.empty:
            return []

        hard_constraints = intent.get("hard_constraints", {})
        soft_preferences = intent.get("soft_preferences", [])
        use_case = intent.get("use_case", [])

        # --------------------------------------------------
        # Fallback if no hard constraints
        # --------------------------------------------------

        structured_fields = ["budget", "category", "brand", "ram_min_gb", "battery_min_mah", "weight_max_kg"]

        no_hard_constraints = all(
    hard_constraints.get(field) is None
    for field in structured_fields
)

        if no_hard_constraints:
            filtered_df = self._keyword_fallback_search(
                self.catalog_df,
                intent
            )
        else:
            filtered_df = self._apply_basic_filters(
                self.catalog_df,
                hard_constraints
            )

        if filtered_df.empty:
            return []

        results = []

        for _, row in filtered_df.iterrows():

            product_dict = row.to_dict()

            spec_data = self._extract_structured_specs(product_dict)

            unmet_structured = self._check_structured_constraints(
                spec_data,
                hard_constraints,
                use_case
            )

            satisfied_hard = self._compute_satisfied_hard_constraints(
                product_dict,
                spec_data,
                hard_constraints
            )

            soft_matches, tradeoffs = self._evaluate_soft_preferences(
                product_dict,
                soft_preferences
            )

            results.append({
                "product_id": product_dict.get("product_id"),
                "product_name": product_dict.get("name"),
                "brand": product_dict.get("brand"),
                "price": product_dict.get("price"),
                "hard_matches": satisfied_hard,
                "soft_matches": soft_matches,
                "tradeoffs": tradeoffs + unmet_structured,
                "unmet_needs": tradeoffs + unmet_structured
            })

        # --------------------------------------------------
        # Intelligent Ranking
        # --------------------------------------------------

        results.sort(
            key=lambda x: (
                len(x["unmet_needs"]),        # fewer unmet first
                -len(x["soft_matches"]),      # more soft matches
                -x.get("price", 0)            # higher spec models next
            )
        )

        return results[:top_k]

    # --------------------------------------------------
    # Basic Hard Filters
    # --------------------------------------------------

    def _apply_basic_filters(
        self,
        df: pd.DataFrame,
        constraints: Dict[str, Any]
    ) -> pd.DataFrame:

        filtered_df = df.copy()

        for key, value in constraints.items():

            if value is None:
                continue

            key_lower = key.lower()

            if key_lower == "budget":
                filtered_df = filtered_df[
                    filtered_df["price"] <= float(value)
                ]

            elif key_lower == "category":
                value_clean = str(value).lower().rstrip("s")
                filtered_df = filtered_df[
                    filtered_df["category"]
                    .astype(str)
                    .str.lower()
                    .str.rstrip("s")
                    .str.contains(value_clean, na=False)
                ]

            elif key_lower == "brand":

             value_clean = str(value).lower()

             filtered_df = filtered_df[
        (
            filtered_df["brand"]
            .astype(str)
            .str.lower()
            .str.contains(value_clean, na=False)
        )
        |
        (
            filtered_df["name"]
            .astype(str)
            .str.lower()
            .str.contains(value_clean, na=False)
        )
    ]


        return filtered_df

    # --------------------------------------------------
    # Generic Keyword Fallback Search
    # --------------------------------------------------

    def _keyword_fallback_search(
        self,
        df: pd.DataFrame,
        intent: Dict[str, Any]
    ) -> pd.DataFrame:

        query_terms = []

        # Collect structured text
        query_terms.extend(intent.get("soft_preferences", []))
        query_terms.extend(intent.get("use_case", []))

        original_query = intent.get("original_query", "")
        if original_query:
            query_terms.extend(original_query.lower().split())

        if not query_terms:
            return df.head(0)

        searchable_columns = ["name", "brand", "category"]

        mask = True

        for term in query_terms:

            term_mask = False

            for col in searchable_columns:
                 term_mask = term_mask | df[col].astype(str).str.lower().str.contains(term, na=False)

            mask = mask & term_mask

        return df[mask]
    # --------------------------------------------------
    # Structured Spec Extraction
    # --------------------------------------------------

    def _extract_structured_specs(self, product: Dict[str, Any]) -> Dict[str, Any]:

        text = " ".join([
            str(product.get("specifications", "")),
            str(product.get("features", ""))
        ]).lower()

        specs = {}

        # RAM: matches "RAM: 16GB"
        ram_match = re.search(r"ram[:\s]*?(\d+)\s?gb", text)
        if ram_match:
            specs["ram_gb"] = int(ram_match.group(1))

        # Battery: matches "5000mAh"
        battery_match = re.search(r"(\d+)\s?mah", text)
        if battery_match:
            specs["battery_mah"] = int(battery_match.group(1))

        # Weight: matches "1.5kg"
        weight_match = re.search(r"(\d+(\.\d+)?)\s?kg", text)
        if weight_match:
            specs["weight_kg"] = float(weight_match.group(1))

        return specs

    # --------------------------------------------------
    # Structured Constraint Checking
    # --------------------------------------------------

    def _check_structured_constraints(
        self,
        specs: Dict[str, Any],
        constraints: Dict[str, Any],
        use_case: List[str]
    ) -> List[str]:

        unmet = []

        if constraints.get("ram_min_gb"):
            if specs.get("ram_gb", 0) < constraints["ram_min_gb"]:
                unmet.append("ram requirement not met")

        if constraints.get("battery_min_mah"):
            if specs.get("battery_mah", 0) < constraints["battery_min_mah"]:
                unmet.append("battery requirement not met")

        if constraints.get("weight_max_kg"):
            if specs.get("weight_kg", 999) > constraints["weight_max_kg"]:
                unmet.append("weight limit exceeded")

        for case in use_case:

            if case == "coding":
                if specs.get("ram_gb", 0) < 8:
                    unmet.append("insufficient ram for coding")

            elif case == "gaming":
                if specs.get("ram_gb", 0) < 16:
                    unmet.append("insufficient ram for gaming")

        return unmet

    # --------------------------------------------------
    # Compute Satisfied Hard Constraints
    # --------------------------------------------------

    def _compute_satisfied_hard_constraints(
        self,
        product: Dict[str, Any],
        specs: Dict[str, Any],
        constraints: Dict[str, Any]
    ) -> List[str]:

        satisfied = []

        for k, v in constraints.items():

            if v is None:
                continue

            if k == "budget":
                if product.get("price", 999999) <= float(v):
                    satisfied.append(k)

            elif k == "category":
                satisfied.append(k)

            elif k == "brand":
                satisfied.append(k)

            elif k == "ram_min_gb":
                if specs.get("ram_gb", 0) >= v:
                    satisfied.append(k)

            elif k == "battery_min_mah":
                if specs.get("battery_mah", 0) >= v:
                    satisfied.append(k)

            elif k == "weight_max_kg":
                if specs.get("weight_kg", 999) <= v:
                    satisfied.append(k)

        return satisfied

    # --------------------------------------------------
    # Soft Matching
    # --------------------------------------------------

    def _evaluate_soft_preferences(
        self,
        product: Dict[str, Any],
        soft_preferences: List[str]
    ) -> Tuple[List[str], List[str]]:

        matches: List[str] = []
        tradeoffs: List[str] = []

        searchable_text = " ".join([
            str(product.get("description", "")),
            str(product.get("specifications", "")),
            str(product.get("features", ""))
        ]).lower()

        searchable_text = re.sub(r"[^a-z0-9\s]", " ", searchable_text)

        for pref in soft_preferences:

            pref_clean = re.sub(r"[^a-z0-9\s]", " ", pref.lower())
            pref_tokens = pref_clean.split()

            token_matches = sum(
                1 for token in pref_tokens if token in searchable_text
            )

            if token_matches >= 1:
                matches.append(pref)
            else:
                tradeoffs.append(pref)

        return matches, tradeoffs
