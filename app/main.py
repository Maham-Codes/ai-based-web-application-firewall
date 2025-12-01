"""
Flask application: serves HTML and exposes API endpoints.
"""
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import datetime
from .utils.detector import detect_request
from .db import init_db, insert_log, get_latest_logs

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# initialize DB
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def logs_page():
    return render_template('logs.html')

@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    data = request.json or {}
    input_text = data.get('input', '')
    ip = request.remote_addr or 'unknown'
    ts = datetime.datetime.utcnow().isoformat()

    detection = detect_request(input_text)
    result = detection.get('result', 'Unknown')
    reason = detection.get('reason', '')

    insert_log(ts, ip, input_text, result, reason)

    return jsonify({'result': result, 'reason': reason})

@app.route('/api/logs')
def api_logs():
    rows = get_latest_logs(200)
    logs = [{'ts': r[0], 'ip': r[1], 'input': r[2], 'result': r[3], 'reason': r[4]} for r in rows]
    return jsonify(logs)

@app.route('/api/stats')
def api_stats():
    # compute simple stats from latest logs (in memory query)
    rows = get_latest_logs(1000)
    total = len(rows)
    malicious = sum(1 for r in rows if r[3] == 'Malicious')
    safe = sum(1 for r in rows if r[3] == 'Safe')
    return jsonify({'total': total, 'malicious': malicious, 'safe': safe})

if __name__ == '__main__':
    # run flask app directly
    app.run(debug=True)