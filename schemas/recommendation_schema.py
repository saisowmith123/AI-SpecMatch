from pydantic import BaseModel
from typing import List, Optional, Dict


class RecommendationSchema(BaseModel):

    # Core Identity
    product_name: str
    brand: Optional[str] = None
    price: Optional[float] = None

    # Matching Transparency
    hard_matches: List[str]
    soft_matches: List[str]
    tradeoffs: List[str]
    unmet_needs: List[str]

    # Use-case alignment
    use_case: Optional[List[str]] = None

    # Explanation Layer
    explanation: Optional[str] = None

    # Enrichment Layer
    availability: Optional[str] = None
    rating: Optional[float] = None
    offer: Optional[str] = None
    review_snippets: Optional[List[str]] = None

    # Evaluation Layer
    evaluation: Optional[Dict] = None

    # Gap Detection Layer
    gap_analysis: Optional[Dict] = None
