import pandas as pd
import random
import re
from typing import Dict, Any, List

from config import PRODUCT_CATALOG_PATH
from utils import get_logger

logger = get_logger(__name__)


class Enricher:
    """
    Enrich recommendations using product_catalog.csv:

    Adds:
    - availability
    - rating
    - review_snippets (derived from description/features)
    - simple offer logic
    """

    def __init__(self, catalog_path: str | None = None):
        self.catalog_path = catalog_path or PRODUCT_CATALOG_PATH
        self.catalog_df = self._load_catalog()

    # --------------------------------------------------
    # Load Catalog
    # --------------------------------------------------

    def _load_catalog(self) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.catalog_path)
            logger.info(f"Catalog loaded with {len(df)} products.")
            return df
        except Exception as e:
            logger.error(f"Failed to load catalog: {e}")
            return pd.DataFrame()

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def enrich(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:

        product_id = recommendation.get("product_id")

        if self.catalog_df.empty or product_id is None:
            return recommendation

        product_row = self.catalog_df[
            self.catalog_df["product_id"] == product_id
        ]

        if product_row.empty:
            return recommendation

        product_data = product_row.iloc[0]

        stock_count = product_data.get("stock_count", 0)
        rating = product_data.get("rating")

        availability = "In Stock" if stock_count > 0 else "Out of Stock"

        # Generate review snippets from description/features
        review_snippets = self._generate_review_snippets(product_data)

        # Simple offer logic
        offer = self._generate_offer(stock_count, rating)

        enriched_data = {
            "availability": availability,
            "rating": rating,
            "review_snippets": review_snippets,
            "offer": offer
        }

        recommendation.update(enriched_data)

        return recommendation

    def enrich_batch(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:

        return [self.enrich(rec) for rec in recommendations]

    # --------------------------------------------------
    # Review Snippet Generator
    # --------------------------------------------------

    def _generate_review_snippets(self, product_row: pd.Series) -> List[str]:

        text = " ".join([
            str(product_row.get("description", "")),
            str(product_row.get("features", ""))
        ])

        sentences = re.split(r"[.]", text)

        cleaned = [
            s.strip() for s in sentences
            if len(s.strip()) > 20
        ]

        if not cleaned:
            return []

        # Return up to 2 snippets
        return random.sample(cleaned, min(2, len(cleaned)))

    # --------------------------------------------------
    # Offer Logic
    # --------------------------------------------------

    def _generate_offer(self, stock_count: int, rating: float) -> str | None:

        if stock_count <= 5:
            return "Limited stock available"

        if rating and rating >= 4.5:
            return "Top rated product"

        return None
