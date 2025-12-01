AI-Based Web Application Firewall (Academic Project)

Structure: A Flask backend with a basic HTML/CSS frontend (no JS framework). Demonstrates:
 - Detection for SQLi, XSS, path traversal, command injection, and malicious URL patterns using simple heuristics + ML.
 - Logs stored in SQLite (app/logs.db).
 - Dashboard with live logs and stats (polling every 3s).

How to run:
1. Create a Python virtual environment and activate it.
   python -m venv venv
   # Linux/Mac
   source venv/bin/activate
   # Windows (PowerShell)
   .\\venv\\Scripts\\Activate.ps1
   # Windows (cmd)
   .\\venv\\Scripts\\activate

2. Install requirements:
   pip install -r requirements.txt

3. Train the sample model (creates app/models/waf_model.pkl):
   python train_model.py

4. Run the Flask app:
   # run directly
   python -m app.main
   # or
   export FLASK_APP=app.main
   export FLASK_ENV=development
   flask run

5. Open http://127.0.0.1:5000/

Notes:
 - This is an academic demo. For production you must add authentication, TLS, stricter sanitization, rate-limiting, deployment hardening, and more training data.
