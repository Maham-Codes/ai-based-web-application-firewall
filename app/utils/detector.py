# ============================
# detector.py (FINAL VERSION)
# ============================

import re
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "waf_model.pkl"
_model = None

# ---------------------------------
# RULE-BASED DETECTION (SAFE + ACCURATE)
# ---------------------------------
RULES = [
    # SQL Injection — only real SQL syntax, not normal words
    (re.compile(r"(?i)\bselect\s+\*?\s+from\b"), "SQL Injection Pattern"),
    (re.compile(r"(?i)\bunion\s+select\b"), "SQL Injection Pattern"),
    (re.compile(r"(?i)\'\s*or\s*\'1\'=\'1"), "SQL Injection Pattern"),

    # XSS — only true JS/script patterns
    (re.compile(r"(?i)<script[^>]*>"), "XSS Pattern"),
    (re.compile(r"(?i)onerror\s*="), "XSS Pattern"),
    (re.compile(r"(?i)alert\s*\("), "XSS Pattern"),

    # Path Traversal — real traversal attempts
    (re.compile(r"\.\./|\.\.\\|/etc/passwd|/etc/shadow"), "Path Traversal"),

    # Command Injection — ONLY dangerous patterns
    (re.compile(r"(?i)(;\s*(rm|wget|curl)\b)"), "Command Injection"),
    (re.compile(r"(?i)\bexec\s*\("), "Command Injection"),
    (re.compile(r"(?i)(&&\s*\w+)"), "Command Injection")
]

# ---------------------------------
# ML threshold (Higher = fewer false positives)
# ---------------------------------
ML_THRESHOLD = 0.90


def _load_model():
    global _model
    if _model is None:
        if MODEL_PATH.exists():
            _model = joblib.load(MODEL_PATH)
        else:
            _model = None
    return _model


def clean_text(t: str):
    """Basic normalization for better ML predictions."""
    if not t:
        return ""
    return t.strip().lower()


def detect_request(text: str):
    # Normalize + pad with headers so it matches training structure
    text = clean_text(text)

    text = (
    "URL=" + text + " " +
    "Method=GET User-Agent=Mozilla/5.0 Accept=text/html"
           )

    # -----------------------
    # 1. RULE-BASED DETECTION
    # -----------------------
    for pattern, reason in RULES:
        if pattern.search(text):
            return {
                "result": "Malicious",
                "reason": reason,
                "score": 1.0
            }

    # -----------------------
    # 2. ML CLASSIFICATION
    # -----------------------
    model = _load_model()
    if model is not None:
        try:
            proba = float(model.predict_proba([text])[0][1])  # probability of malicious

            if proba >= ML_THRESHOLD:
                return {
                    "result": "Malicious",
                    "reason": "ML Classification",
                    "score": proba
                }
            else:
                return {
                    "result": "Safe",
                    "reason": "ML Classification",
                    "score": proba
                }

        except Exception as e:
            return {"result": "Unknown", "reason": f"Model error: {e}", "score": 0.0}

    # -----------------------
    # If model missing
    # -----------------------
    return {"result": "Safe", "reason": "No Model Loaded", "score": 0.0}
