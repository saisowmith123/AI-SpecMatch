import logging
import re
import json
from pathlib import Path
from typing import Any, Dict, Optional


# --------------------------------------------------
# Logger
# --------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s'
    )
    return logging.getLogger(name)


# --------------------------------------------------
# File Utilities
# --------------------------------------------------

def load_file(file_path: Path | str) -> str:
    """Load and return file contents as string."""
    return Path(file_path).read_text(encoding="utf-8").strip()


def ensure_directory(path: Path | str) -> None:
    """Create directory if it does not exist."""
    Path(path).mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# JSON Utilities
# --------------------------------------------------

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extract JSON object from LLM output text.
    Returns empty dict if extraction fails.
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {}
    except json.JSONDecodeError:
        return {}


def safe_json_loads(text: str) -> Optional[Dict[str, Any]]:
    """Safely load JSON string."""
    try:
        return json.loads(text)
    except Exception:
        return None


# --------------------------------------------------
# Scoring Utilities
# --------------------------------------------------

def normalize_score(value: float, min_value: float, max_value: float) -> float:
    """Normalize a numeric value between 0 and 1."""
    if max_value == min_value:
        return 0.0
    return (value - min_value) / (max_value - min_value)


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    """Clamp a value within bounds."""
    return max(min_value, min(max_value, value))
