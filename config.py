import os
from pathlib import Path
from dotenv import load_dotenv

# --------------------------------------------------
# Project Root & Environment
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).parent
load_dotenv(PROJECT_ROOT / ".env")

# --------------------------------------------------
# API Configuration
# --------------------------------------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Optional fallback

DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "gemini")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")

MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY = int(os.getenv("RETRY_DELAY", 2))

# --------------------------------------------------
# Data Paths
# --------------------------------------------------

DATA_DIR = PROJECT_ROOT / "data"
PRODUCT_CATALOG_PATH = DATA_DIR / "product_catalog.csv"
USER_PROFILE_PATH = DATA_DIR / "user_profiles.csv"

# --------------------------------------------------
# Matching & Recommendation Settings
# --------------------------------------------------

TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", 5))
MIN_MATCH_SCORE = float(os.getenv("MIN_MATCH_SCORE", 0.5))

ENABLE_SOFT_MATCHING = os.getenv("ENABLE_SOFT_MATCHING", "true").lower() == "true"
ENABLE_ENRICHMENT = os.getenv("ENABLE_ENRICHMENT", "true").lower() == "true"

# --------------------------------------------------
# Evaluation Settings
# --------------------------------------------------

DEFAULT_BATCH_SIZE = int(os.getenv("DEFAULT_BATCH_SIZE", 10))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
