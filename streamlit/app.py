import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import streamlit as st
import pandas as pd

from pipeline.recommender.recommender import Recommender
from evaluate import calculate_metrics

st.set_page_config(page_title="SpecSense AI", layout="wide")
st.title("SpecSense AI")

recommender = Recommender()

# --------------------------------------------------
# Tabs
# --------------------------------------------------

tab1, tab2 = st.tabs(["Single Recommendation", "Evaluation"])

# ==================================================
# 1️⃣ Single Query Mode
# ==================================================

with tab1:

    st.header("Product Recommendation")

    user_query = st.text_area(
        "Enter your requirement:",
        height=120,
        placeholder="Example: Lightweight laptop under 30000 with 16GB RAM for coding"
    )

    user_id_input = st.text_input("User ID (optional):")


    if st.button("Get Recommendations", type="primary"):

        if not user_query.strip():
            st.warning("Please enter a query.")
        else:
            # try:
            #     user_id = int(user_id_input) if user_id_input.strip() else None
            # except ValueError:
            #     st.error("User ID must be an integer.")
            #     user_id = None

            user_id = user_id_input.strip() if user_id_input.strip() else None

            with st.spinner("Analyzing and matching products..."):
                results = recommender.recommend(
                    user_query=user_query,
                    user_id=user_id
                )

            if not results:
                st.error("No suitable products found.")
            else:
                st.success("Recommendations generated!")

                for idx, product in enumerate(results, start=1):

                    st.markdown("---")
                    st.subheader(f"{idx}. {product.get('product_name')}")

                    col1, col2, col3 = st.columns(3)

                    col1.metric("Brand", product.get("brand"))
                    col2.metric("Price", f"₹{product.get('price')}")
                    col3.metric("Rating", product.get("rating"))

                    # Availability
                    availability = product.get("availability")
                    if availability == "In Stock":
                        st.success("In Stock")
                    else:
                        st.error("Out of Stock")

                    # Hard Matches
                    hard = product.get("hard_matches", [])
                    if hard:
                        st.markdown("**Hard Constraints Met:**")
                        st.markdown(", ".join(hard))

                    # Soft Matches
                    soft = product.get("soft_matches", [])
                    if soft:
                        st.markdown("**Soft Matches:**")
                        st.markdown(", ".join(soft))

                    # Trade-offs
                    tradeoffs = product.get("tradeoffs", [])
                    if tradeoffs:
                        st.markdown("**Trade-offs:**")
                        st.markdown(", ".join(tradeoffs))

                    # Explanation
                    with st.expander("Why this product?"):
                        st.write(product.get("explanation", ""))

                    # Review snippets (if available)
                    reviews = product.get("review_snippets", [])
                    if reviews:
                        with st.expander("Customer Insights"):
                            for r in reviews:
                                st.write(f"- {r}")

                    # Score
                    evaluation = product.get("evaluation", {})
                    score = evaluation.get("overall_score", 0)
                    st.progress(score)
                    st.caption(f"Overall Match Score: {score}")

# ==================================================
# 2️⃣ Evaluation Mode
# ==================================================

with tab2:

    st.header("Evaluate Recommendation Quality")
    st.caption("Test recommendation accuracy using a dataset of queries and expected products.")

    uploaded_file = st.file_uploader("Upload Evaluation CSV with columns: query, expected_product", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        required_cols = {"query", "expected_product"}

        if not required_cols.issubset(set(df.columns)):
            st.error("CSV must contain 'query' and 'expected_product' columns.")
        else:
            st.success(f"Loaded {len(df)} rows.")

            limit = st.number_input(
                "Limit rows for testing",
                min_value=1,
                max_value=len(df),
                value=min(20, len(df))
            )

            if st.button("Run Evaluation", type="primary"):
                with st.spinner("Running evaluation..."):

                    queries = df["query"].tolist()[:limit]
                    expected = df["expected_product"].tolist()[:limit]

                    predictions = []

                    for query in queries:
                        results = recommender.recommend(query)
                        if results:
                            predictions.append(results[0]["product_name"])
                        else:
                            predictions.append("None")

                    metrics = calculate_metrics(expected, predictions)

                st.success("Evaluation complete!")

                col1, col2, col3 = st.columns(3)
                col1.metric("Accuracy", f"{metrics['accuracy']}%")
                col2.metric("Correct", metrics["correct"])
                col3.metric("Total", metrics["total"])
