# AI SpecMatch

AI SpecMatch is a smart product discovery tool that helps users find products by describing what they need in plain English. Instead of manually applying filters, users can type requests like “lightweight laptop under $900 with good battery life,” and the system returns suitable product matches from a structured catalog.

## Features

- Search products using natural language
- Converts user queries into structured product preferences
- Filters catalog data based on important requirements
- Ranks products based on how well they match the request
- Explains why each product was recommended
- Identifies missing or unmatched requirements
- Supports single-query and CSV-based batch analysis
- Includes a simple Streamlit interface

## Tech Stack

- Python
- Streamlit
- Google Gemini API
- Pandas
- Pydantic

## How to Run

Clone the repository.

Install dependencies:

pip install -r requirements.txt

Create a `.env` file and add:

GEMINI_API_KEY=your_api_key_here

Run the app:

streamlit run streamlit_app/app.py

## Summary

AI SpecMatch makes product search easier by combining natural language input with catalog-based matching. It focuses on giving users relevant recommendations along with clear reasons behind each match.
