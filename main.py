from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from pipeline.recommender.recommender import Recommender
from utils import get_logger

logger = get_logger(__name__)


def main():
    """
    CLI entry point for SpecSense AI
    """

    print("\n=== SpecSense AI ===")
    print("Provide your user ID and product requirement.\n")

    try:
        user_id_input = input("Enter User ID (or press Enter to skip): ").strip()
        user_id = user_id_input if user_id_input else None
    except ValueError:
        print("Invalid user ID.")
        return

    user_query = input("Enter your query: ").strip()

    if not user_query:
        print("No query provided. Exiting.")
        return

    try:
        recommender = Recommender()

        results = recommender.recommend(
            user_query=user_query,
            user_id=user_id
        )

        print("\n==============================")
        print("RECOMMENDATION RESULTS")
        print("==============================\n")

        if not results:
            print("No suitable products found.")
            return

        for idx, product in enumerate(results, start=1):
            print(f"{idx}. {product.get('product_name')}")
            print(f"   Brand        : {product.get('brand')}")
            print(f"   Price        : {product.get('price')}")
            print(f"   Availability : {product.get('availability')}")
            print(f"   Rating       : {product.get('rating')}")
            print(f"   Hard Matches : {product.get('hard_matches')}")
            print(f"   Soft Matches : {product.get('soft_matches')}")
            print(f"   Trade-offs   : {product.get('tradeoffs')}")
            print(f"   Explanation  : {product.get('explanation')}")
            print(f"   Score        : {product.get('evaluation', {}).get('overall_score')}")
            print("-" * 50)

    except Exception as e:
        logger.error(f"Recommendation failed: {e}")
        print(f"\nError: {e}")


if __name__ == "__main__":
    main()
