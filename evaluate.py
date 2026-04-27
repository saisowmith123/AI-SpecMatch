import argparse
import pandas as pd
from typing import List, Dict, Any

from pipeline.recommender.recommender import Recommender
from utils import get_logger
from config import PRODUCT_CATALOG_PATH

logger = get_logger(__name__)


# --------------------------------------------------
# Evaluation Metrics
# --------------------------------------------------

def calculate_metrics(actual: List[str], predicted: List[str]) -> Dict[str, Any]:
    total = len(actual)
    if total == 0:
        return {
            "total": 0,
            "correct": 0,
            "accuracy": 0.0
        }

    actual_clean = [a.strip().lower() for a in actual]
    predicted_clean = [p.strip().lower() for p in predicted]

    correct = sum(1 for a, p in zip(actual_clean, predicted_clean) if a == p)
    accuracy = (correct / total) * 100

    return {
        "total": total,
        "correct": correct,
        "accuracy": round(accuracy, 2)
    }


# --------------------------------------------------
# Evaluation Runner
# --------------------------------------------------

def evaluate_model(dataset_path: str, limit: int | None = None):
    try:
        df = pd.read_csv(dataset_path)
        print(f"Loaded dataset with {len(df)} rows")
    except FileNotFoundError:
        print(f"Dataset not found at {dataset_path}")
        return

    required_columns = {"query", "expected_product"}
    if not required_columns.issubset(set(df.columns)):
        print("Dataset must contain 'query' and 'expected_product' columns.")
        return

    if limit:
        df = df.head(limit)
        print(f"Limiting to first {limit} rows.")

    recommender = Recommender()

    queries = df["query"].tolist()
    expected = df["expected_product"].tolist()

    predictions: List[str] = []

    for idx, query in enumerate(queries, start=1):
        try:
            results = recommender.recommend(query)
            if results:
                top_product = results[0].get("product_name", "None")
            else:
                top_product = "None"

            predictions.append(top_product)

        except Exception as e:
            logger.error(f"Failed at row {idx}: {e}")
            predictions.append("None")

    metrics = calculate_metrics(expected, predictions)

    print("\n" + "=" * 40)
    print("EVALUATION RESULTS")
    print("=" * 40)
    print(f"Total Queries   : {metrics['total']}")
    print(f"Correct Matches : {metrics['correct']}")
    print(f"Accuracy        : {metrics['accuracy']}%")
    print("=" * 40)


# --------------------------------------------------
# CLI
# --------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate SpecSense AI")
    parser.add_argument("dataset", help="Path to evaluation CSV file")
    parser.add_argument("--limit", type=int, help="Limit number of rows")

    args = parser.parse_args()

    evaluate_model(args.dataset, args.limit)
