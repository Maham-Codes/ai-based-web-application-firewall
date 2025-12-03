import os
import re
import random
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report, confusion_matrix,
    f1_score, accuracy_score, roc_auc_score
)
from sklearn.utils import shuffle

RND = 42
random.seed(RND)
np.random.seed(RND)

# -----------------------------------------
# Helper: Extract only PATH from URL
# -----------------------------------------
def extract_path(url):
    url = str(url)
    match = re.search(r"http[s]?://[^/]+(/.*)", url)
    return match.group(1) if match else url

# -----------------------------------------
# FIXED: Safe URL generator (robust)
# -----------------------------------------
def generate_safe_url_templates():
    base_paths = [
        "/home", "/index.php", "/products", "/product/view",
        "/cart/add", "/user/profile", "/account/settings",
        "/search", "/blog/article", "/api/items",
        "/api/user", "/checkout", "/category", "/contact",
        "/about", "/login", "/logout", "/register"
    ]

    params = [
        "?id={}", "?q={}", "?page={}", "?page={}&sort=asc", "?cat={}&p={}"
    ]

    words = ["apple","book","phone","toy","shirt","camera","code","safe","normal","testing"]

    urls = set()

    for b in base_paths:
        urls.add(b)

        for p in params:
            count = p.count("{}")
            if count == 0:
                urls.add(b + p)
            elif count == 1:
                val = random.choice(words)
                urls.add(b + p.format(val))
            elif count == 2:
                v1 = random.choice(words)
                v2 = random.choice(words)
                urls.add(b + p.format(v1, v2))

    # deeper safe URLs
    for _ in range(300):
        b = random.choice(base_paths)
        depth = "/".join(random.choices(words, k=random.randint(1, 3)))
        urls.add(f"{b}/{depth}")

    return list(urls)

# -----------------------------------------
# Generate safe ENGLISH sentences
# -----------------------------------------
def generate_safe_sentences(n=300):
    starts = ["hello", "hi", "this is", "i am", "please", "kindly"]
    middles = ["a safe request", "normal text", "not malicious", "a student", "testing the firewall"]
    ends = ["thank you", "just testing", "please allow", "open homepage", "nothing harmful here"]

    sentences = []
    for _ in range(n):
        s = f"{random.choice(starts)} {random.choice(middles)} {random.choice(ends)}"
        sentences.append(s)
    return sentences

# -----------------------------------------
# Malicious payload generators
# -----------------------------------------
def mutate_malicious(payload):
    v = payload
    if random.random() < 0.4:
        v = v.replace(" ", "%20").replace("'", "%27")
    if random.random() < 0.3:
        v = "".join(c.upper() if random.random() < 0.5 else c for c in v)
    if random.random() < 0.3:
        v = v.replace(" ", "/* */")
    return v

def generate_malicious_variants():
    base = [
        "SELECT * FROM users WHERE id=1",
        "' OR '1'='1",
        "UNION SELECT username, password FROM accounts",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "; rm -rf /",
        "| cat /etc/shadow",
        "`cat /etc/passwd`",
        "exec('ls')",
        "system('rm -rf *')",
        "sleep(10)",
    ]

    variants = []
    for p in base:
        variants.append(p)
        for _ in range(7):
            variants.append(mutate_malicious(p))

    # shallow SQL variants
    for _ in range(200):
        col = random.choice(["name", "id", "email", "password"])
        tbl = random.choice(["users", "accounts", "orders"])
        q = f"SELECT {col} FROM {tbl} WHERE {col} LIKE '%a%'"
        variants.append(q)

    return list(set(variants))

# -----------------------------------------
# Load CSIC dataset
# -----------------------------------------
print("Loading CSIC dataset...")
df = pd.read_csv("csic_database.csv", low_memory=False)

df["clean_url"] = df["URL"].astype(str).apply(extract_path)
csic_text = df["clean_url"]
csic_labels = df["classification"].astype(int)

print("CSIC samples:", len(csic_text))

# -----------------------------------------
# Build synthetic safe + malicious
# -----------------------------------------
safe_urls = generate_safe_url_templates()
safe_sentences = generate_safe_sentences(400)
api_safe = [f'{{"action":"get","id":{random.randint(1,400)}}}' for _ in range(200)]
safe_samples = list(set(safe_urls + safe_sentences + api_safe))

malicious_samples = generate_malicious_variants()

# -----------------------------------------
# Merge everything
# -----------------------------------------
texts = pd.concat([csic_text, pd.Series(safe_samples), pd.Series(malicious_samples)], ignore_index=True)
labels = pd.concat([csic_labels, pd.Series([0]*len(safe_samples)), pd.Series([1]*len(malicious_samples))], ignore_index=True)

texts, labels = shuffle(texts, labels, random_state=RND)

print("Final dataset size:", texts.shape)
print("Labels:", labels.value_counts())

# -----------------------------------------
# Split into Train, Validation, Test
# -----------------------------------------
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.10, random_state=RND, stratify=labels)
X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.12, random_state=RND, stratify=y_train)

# -----------------------------------------
# Build Pipeline
# -----------------------------------------
pipe = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=15000,
        ngram_range=(1, 3),
        min_df=2,
        max_df=0.95,
        token_pattern=r"[^ ]+"
    )),
    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", solver="saga"))
])

pipe.fit(X_train, y_train)

# -----------------------------------------
# Threshold tuning
# -----------------------------------------
val_probs = pipe.predict_proba(X_val)[:,1]

best_thr = 0.5
best_f1 = 0

for thr in np.linspace(0.2, 0.95, 60):
    preds = (val_probs >= thr).astype(int)
    f1 = f1_score(y_val, preds)
    if f1 > best_f1:
        best_f1 = f1
        best_thr = thr

print(f"\nChosen threshold: {best_thr:.3f} (F1={best_f1:.4f})")

# -----------------------------------------
# Final evaluation
# -----------------------------------------
test_probs = pipe.predict_proba(X_test)[:,1]
test_preds = (test_probs >= best_thr).astype(int)

print("\n===== FINAL MODEL EVALUATION =====\n")
print("Accuracy:", accuracy_score(y_test, test_preds))
print("ROC-AUC:", roc_auc_score(y_test, test_probs))
print(classification_report(y_test, test_preds))
print("Confusion Matrix:")
print(confusion_matrix(y_test, test_preds))

# -----------------------------------------
# Save model + threshold
# -----------------------------------------
os.makedirs("app/models", exist_ok=True)
joblib.dump(pipe, "app/models/waf_model.pkl")

with open("app/models/waf_threshold.txt", "w") as f:
    f.write(str(best_thr))

print("\nModel saved to app/models/waf_model.pkl")
print("Threshold saved to app/models/waf_threshold.txt")
print("Training complete.")
