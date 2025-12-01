# ============================
# detector.py (FULL FILE)
# ============================

import re
import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "waf_model.pkl"
_model = None

# ---------------------------------
# RULE-BASED DETECTION
# ---------------------------------
RULES = [
    # SQL Injection — ONLY when SQL syntax is used
    (re.compile(r"(?i)(\bselect\b\s+\*?\s*\bfrom\b|\bunion\b|\'\s*or\s*\'1\'=\'1|--|;|/\*)"), "SQL Injection Pattern"),

    # XSS
    (re.compile(r"(?i)<script>|onerror=|alert\("), "XSS Pattern"),

    # Path Traversal
    (re.compile(r"(\.\./|\.\.\\|/etc/passwd|system32)"), "Path Traversal"),

    # Command Injection
    (re.compile(r"(?i)(rm\s+-rf|;.*rm|system\(|exec\(|wget\s+http)"), "Command Injection")
]


# Probability threshold (tune if needed)
ML_THRESHOLD = 0.82


def _load_model():
    global _model
    if _model is None:
        if MODEL_PATH.exists():
            _model = joblib.load(MODEL_PATH)
        else:
            _model = None
    return _model


def detect_request(text: str):
    text = text or ""

    # 1. RULE-BASED DETECTION
    for pattern, reason in RULES:
        if pattern.search(text):
            return {"result": "Malicious", "reason": reason, "score": 1.0}

    # 2. ML DETECTION
    model = _load_model()
    if model is not None:
        try:
            proba = model.predict_proba([text])[0][1]  # probability malicious
            if proba >= ML_THRESHOLD:
                return {"result": "Malicious", "reason": "ML Classification", "score": float(proba)}
            else:
                return {"result": "Safe", "reason": "ML Classification", "score": float(proba)}

        except Exception as e:
            return {"result": "Unknown", "reason": f"Model error: {e}", "score": 0.0}

    # No model fallback
    return {"result": "Safe", "reason": "No Model Loaded", "score": 0.0}
