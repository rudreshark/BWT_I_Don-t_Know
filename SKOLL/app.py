
try:
    import eventlet
    eventlet.monkey_patch()
except Exception:
    pass

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime, timedelta
from flask_socketio import SocketIO, emit, join_room
import numpy as np
import pandas as pd

app = Flask(__name__)
app.secret_key = os.urandom(24)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

online_agents = {}

def evaluate_malicious_activity(data):
    score = 0.0
    p = (data.get('process_name') or '').lower()
    a = (data.get('action') or '').lower()
    f = (data.get('file_name') or '').lower()
    if 'upload' in a or 'download' in a:
        score += 0.2
    if any(x in f for x in ['.exe', '.bat', '.ps1']):
        score += 0.4
    if any(x in p for x in ['powershell', 'cmd', 'curl']):
        score += 0.3
    if data.get('cpu_usage', 0) > 80:
        score += 0.3
    if score < 0:
        score = 0.0
    if score > 1:
        score = 1.0
    return score

def compute_behavior():
    conn = get_db_connection()
    logs = pd.read_sql_query("SELECT user_id, process_name, cpu_usage, ts FROM system_logs ORDER BY ts DESC LIMIT 500", conn)
    if logs.empty:
        conn.close()
        return
    # Baseline distribution
    baseline = logs['process_name'].value_counts(normalize=True)
    # Current distribution per user
    for uid, df in logs.groupby('user_id'):
        dist = df['process_name'].value_counts(normalize=True)
        # Align distributions
        all_idx = sorted(set(baseline.index) | set(dist.index))
        p = np.array([baseline.get(i, 1e-6) for i in all_idx])
        q = np.array([dist.get(i, 1e-6) for i in all_idx])
        p = p / p.sum()
        q = q / q.sum()
        kl = float(np.sum(q * np.log(q / p)))
        cpu = float(df['cpu_usage'].fillna(0).mean())
        drift_score = min(100.0, kl * 50 + cpu * 0.5)
        trust_score = max(0.0, 100.0 - drift_score)
        ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action = 'None'
        conn.execute("INSERT INTO behavior_scores (ts, user_id, drift_score, trust_score, action_taken) VALUES (?, ?, ?, ?, ?)",
                     (ts_now, uid, drift_score, trust_score, action))
        conn.execute("UPDATE users SET drift_score = ?, trust_score = ? WHERE id = ?", (drift_score, trust_score, uid))
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))
    return render_template('index.html')

@app.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if role == 'admin':
            if username == 'admin' and password == 'admin':
                session['user_id'] = 0
                session['role'] = 'admin'
                return redirect(url_for('admin_dashboard'))
            return render_template('login.html', role=role, error='Invalid credentials')
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND role = ?', (username, role)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            conn2 = get_db_connection()
            new_session_count = (user['session_count'] or 0) + 1
            status = user['status']
            if new_session_count > 3:
                status = 'Suspicious'
            conn2.execute('UPDATE users SET session_count = ?, status = ? WHERE id = ?', (new_session_count, status, user['id']))
            conn2.commit()
            conn2.close()

            if status == 'active':
                session['user_id'] = user['id']
                session['role'] = user['role']
                if role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('employee_dashboard'))
            elif status == 'Suspicious':
                return render_template('login.html', role=role, error='Suspicious activity detected. Account locked.')
            else:
                return redirect(url_for('waiting'))
        else:
            return render_template('login.html', role=role, error='Invalid credentials')
    return render_template('login.html', role=role)

@app.route('/register/<role>', methods=['GET', 'POST'])
def register(role):
    if role == 'admin':
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        location = request.form.get('location', '')
        hashed_password = generate_password_hash(password)
        status = 'pending'
        registration_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO users (username, password, role, status, location, registration_time) VALUES (?, ?, ?, ?, ?, ?)',
            (username, hashed_password, role, status, location, registration_time)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('login', role=role))
    return render_template('register.html', role=role)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))

    conn = get_db_connection()
    pending_users = conn.execute('SELECT * FROM users WHERE status = ?', ('pending',)).fetchall()
    suspicious_users = conn.execute('SELECT * FROM users WHERE status = ?', ('Suspicious',)).fetchall()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    return render_template('admin_dash.html',
                           pending_users=pending_users,
                           suspicious_users=suspicious_users,
                           users=users,
                           online_agents=list(online_agents.keys()))

@app.route('/admin/drift')
def drift_page():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))
    return render_template('drift.html')

@app.route('/request_edit', methods=['POST'])
def request_edit():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect(url_for('login', role='employee'))

    location = request.form.get('location', '')
    request_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_db_connection()
    conn.execute('INSERT INTO edit_requests (user_id, request_time, location) VALUES (?, ?, ?)',
                 (session['user_id'], request_time, location))
    conn.commit()
    conn.close()

    return redirect(url_for('employee_dashboard'))

@app.route('/api/ai-score', methods=['POST'])
def ai_score():
    payload = request.get_json(force=True) or {}
    score = evaluate_malicious_activity(payload)
    verdict = 'Approved' if score <= 0.01 else 'Alert'
    er_id = payload.get('edit_request_id')
    token = None
    token_expiry = None
    if er_id:
        conn = get_db_connection()
        if verdict == 'Approved':
            token = os.urandom(16).hex()
            token_expiry = datetime.now() + timedelta(minutes=5)
            conn.execute('UPDATE edit_requests SET status = ?, token = ?, token_expiry = ? WHERE id = ?',
                         ('Approved', token, token_expiry.strftime("%Y-%m-%d %H:%M:%S.%f"), er_id))
        else:
            conn.execute('UPDATE edit_requests SET status = ? WHERE id = ?',
                         ('Alert', er_id))
        conn.commit()
        conn.close()
    socketio.emit('ai_verdict', {'score': score, 'verdict': verdict, 'edit_request_id': er_id}, broadcast=True)
    return jsonify({'score': score, 'verdict': verdict, 'token': token, 'token_expiry': token_expiry})

@app.route('/api/system-log', methods=['POST'])
def system_log():
    data = request.get_json(force=True) or {}
    conn = get_db_connection()
    conn.execute('INSERT INTO system_logs (user_id, process_name, cpu_usage, window_title, ts) VALUES (?, ?, ?, ?, ?)',
                 (data.get('user_id'), data.get('process_name'), data.get('cpu_usage'), data.get('window_title'),
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    socketio.emit('system_log', data, broadcast=True)
    return jsonify({'ok': True})

@app.route('/api/drift-data')
def drift_data():
    conn = get_db_connection()
    users = conn.execute('SELECT id, drift_score, trust_score FROM users').fetchall()
    conn.close()

    data = {
        'labels': [u['id'] for u in users],
        'drift_scores': [u['drift_score'] for u in users],
        'trust_scores': [u['trust_score'] for u in users]
    }
    return jsonify(data)

@app.route('/api/drift-trend')
def drift_trend():
    compute_behavior()
    conn = get_db_connection()
    rows = conn.execute("SELECT ts, drift_score FROM behavior_scores ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    labels = [r['ts'] for r in rows][::-1]
    values = [r['drift_score'] for r in rows][::-1]
    return jsonify({'labels': labels, 'values': values})

@app.route('/api/drift-feed')
def drift_feed():
    compute_behavior()
    conn = get_db_connection()
    rows = conn.execute("SELECT ts, user_id, drift_score, trust_score, action_taken FROM behavior_scores ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/pending-users')
def pending_users_data():
    conn = get_db_connection()
    pending_users = conn.execute('SELECT id, username FROM users WHERE status = ?', ('pending',)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in pending_users])

@app.route('/api/suspicious-users')
def suspicious_users_data():
    conn = get_db_connection()
    suspicious_users = conn.execute('SELECT id, username, session_count FROM users WHERE status = ?', ('Suspicious',)).fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in suspicious_users])

@app.route('/api/edit-requests')
def edit_requests_data():
    conn = get_db_connection()
    edit_requests = conn.execute('SELECT id, user_id, request_time, location, status FROM edit_requests').fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in edit_requests])

@app.route('/block_user/<int:user_id>', methods=['POST'])
def block_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))
    conn = get_db_connection()
    conn.execute('UPDATE users SET status = ? WHERE id = ?', ('Blocked', user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/reset_user/<int:user_id>', methods=['POST'])
def reset_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))
    conn = get_db_connection()
    conn.execute('UPDATE users SET session_count = 0, status = ? WHERE id = ?', ('active', user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/approve_user/<int:user_id>', methods=['POST'])
def approve_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login', role='admin'))
    conn = get_db_connection()
    conn.execute('UPDATE users SET status = ? WHERE id = ?', ('active', user_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/employee')
def employee_dashboard():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect(url_for('login', role='employee'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    if user and user['status'] == 'pending':
        return redirect(url_for('waiting'))
    return render_template('employee_dashboard.html')

@app.route('/workstation/<token>')
def workstation(token):
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect(url_for('login', role='employee'))
    conn = get_db_connection()
    edit_request = conn.execute('SELECT * FROM edit_requests WHERE token = ? AND user_id = ?', (token, session['user_id'])).fetchone()
    conn.close()
    if not edit_request:
        return redirect(url_for('employee_dashboard'))
    try:
        expiry = datetime.strptime(edit_request['token_expiry'], '%Y-%m-%d %H:%M:%S.%f')
    except Exception:
        expiry = datetime.now()
    if datetime.now() > expiry:
        return redirect(url_for('employee_dashboard'))
    return render_template('workstation.html', user_id=session['user_id'], token_expiry=edit_request['token_expiry'])

@app.route('/waiting')
def waiting():
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        if user and user['status'] == 'active':
            return redirect(url_for('employee_dashboard'))
    return render_template('waiting.html')

@socketio.on('agent_hello')
def agent_hello(data):
    uid = data.get('user_id')
    if uid:
        online_agents[str(uid)] = True
        emit('online_users', list(online_agents.keys()), broadcast=True)

@socketio.on('agent_screenshot')
def agent_screenshot(data):
    emit('inspect_stream', data, broadcast=True)

if __name__ == '__main__':
    try:
        import eventlet
        eventlet.monkey_patch()
    except Exception:
        pass
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
