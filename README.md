# 🔥 AI-Based Web Application Firewall (WAF)

A Machine Learning–powered Web Application Firewall built using **Python**, **Flask**, **Scikit-learn**, and **TF-IDF + Logistic Regression**.  
This project detects malicious HTTP requests such as SQL Injection, XSS, Command Injection, and Path Traversal using a hybrid **Rule-Based + Machine Learning** approach.

This project was created as part of an academic semester project.

---

## 🚀 Features

### 🛡 Security Features
- **ML-based malicious request detection**
- **Rule-based detection for:**
  - SQL Injection (`UNION SELECT`, `' OR '1'='1`)
  - Cross-Site Scripting (XSS)
  - Path Traversal (`../../etc/passwd`)
  - Command Injection (`; rm -rf /`)
- **Hybrid detection = high accuracy + fewer false positives**

### 📊 Dashboard Features
- Real-time **Safe vs Malicious** attack chart
- Request log viewer
- Hacker-themed UI (Matrix-style)
- Live auto-refresh every 3 seconds
- API endpoints for automation or external testing

---

## 📁 Dataset

This model uses a combination of:

### 1. CSIC 2010 HTTP Dataset (Open-source)
(https://www.kaggle.com/datasets/ispangler/csic-2010-web-application-attacks)  

Contains:
- **Normal legitimate HTTP requests**
- **Malicious attack requests** crafted against a real webshop

Fields used:
- `URL`  
- `classification` (`0 = Safe`, `1 = Malicious`)

### 2. Synthetic Safe Dataset (Generated)
To improve generalization beyond CSIC:
- Realistic website URLs  
- English text sentences  
- API-like JSON requests  

### 3. Synthetic Malicious Dataset
Includes:
- SQL Injection variants  
- XSS payloads  
- Directory traversal  
- Command execution patterns  
- Obfuscated variants (`%20`, uppercase, comments, etc.)

### Final Dataset Size After Merging
Around **60,000+ samples**, shuffled and balanced.

---

## 🤖 Machine Learning Model

### Model Type
- **TF-IDF Vectorizer (n-gram: 1–3)**
- **Logistic Regression with `class_weight="balanced"`**
- **Threshold tuning via validation set**

### Why Logistic Regression?
- Works well with high-dimensional sparse text data  
- Fast training  
- Easy to tune  
- High accuracy for WAF classification

### Evaluation Metrics
The training script outputs:
- Precision  
- Recall  
- F1-score  
- Confusion Matrix  
- ROC-AUC  
- Tuned probability threshold  
- Saved in `model_evaluation.txt`

---

## 🧠 How to Train the Model

### 1. Ensure `csic_database.csv` exists
Folder structure:

    WAF/
        train_model.py
        csic_database.csv
        app/
        models/
        utils/
        static/
        templates/

### 2. Install dependencies
    pip install -r requirements.txt

### 3. Run training
    python train_model.py

Training will:
- Load CSIC dataset  
- Generate synthetic safe/malicious samples  
- Extract features  
- Train logistic regression  
- Tune threshold  
- Evaluate model  
- Save:
    - app/models/waf_model.pkl  
    - app/models/waf_threshold.txt  
    - model_evaluation.txt

---

## 🚀 How to Run the WAF Application

### 1. Start Flask
    python -m app.main

**Note:** If using `python app/main.py` you must be inside the parent folder to avoid import errors.

### 2. Open browser
Go to: http://127.0.0.1:5000  

You will see:
- Hacker-themed dashboard  
- Request analyzer  
- Real-time safe/malicious pie chart  
- Logs page  
- Settings page  

---

## 🧪 Testing the Firewall

### ✔ SAFE Requests
- /home  
- /search?q=shoes  
- hello how are you  
- /tienda1/publico/anadir.jsp?id=4&nombre=mesa&cantidad=1  
- i am a student testing  

### ❌ MALICIOUS Requests
- SELECT * FROM users  
- ' OR '1'='1  
- <script>alert(1)</script>  
- ../../etc/passwd  
- ; rm -rf /  
- /tienda1/publico/anadir.jsp?id=1 OR '1'='1  

---

## 📂 Project Structure

    WAF/
        train_model.py
        csic_database.csv
        requirements.txt
        model_evaluation.txt
        app/
            main.py
            db.py
            __init__.py
            models/
                waf_model.pkl
                waf_threshold.txt
            utils/
                detector.py
            templates/
                index.html
                logs.html
                settings.html
            static/
                css/style.css
                js/app.js
                js/chart.js

---

## 📝 License
This project is created for **educational purposes** and is not intended for production use.
