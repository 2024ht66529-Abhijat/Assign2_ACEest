from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "aceest_premium_secret"
DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss (FL) – 3 day": {"factor": 22},
    "Fat Loss (FL) – 5 day": {"factor": 24},
    "Muscle Gain (MG) – PPL": {"factor": 35},
    "Beginner (BG)": {"factor": 26},
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        # Drop old tables to avoid schema mismatch in CI/CD
        conn.execute("DROP TABLE IF EXISTS users")
        conn.execute("DROP TABLE IF EXISTS clients")
        conn.execute("DROP TABLE IF EXISTS workouts")
        conn.execute("DROP TABLE IF EXISTS exercises")

        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)")
        conn.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin','admin','Admin')")

        conn.execute("""CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            membership_expiry TEXT
        )""")

        conn.execute("""CREATE TABLE workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT
        )""")

        conn.execute("""CREATE TABLE exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER,
            name TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )""")

    
@app.route('/')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    return render_template('dashboard.html', programs=PROGRAMS, role=session['role'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user, pw = request.form.get('username'), request.form.get('password')
        with get_db() as conn:
            row = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw)).fetchone()
            if row:
                session['user'], session['role'] = row['username'], row['role']
                return redirect(url_for('dashboard'))
        return "Invalid Login"
    return render_template('login.html')

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    name, prog, weight = data.get('name'), data.get('program'), float(data.get('weight', 0) or 0)
    factor = PROGRAMS.get(prog, {'factor': 25})['factor']
    calories = int(weight * factor) if weight > 0 else 0

    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO clients (name,age,height,weight,program,calories) VALUES (?,?,?,?,?,?)",
                     (name, data.get('age'), data.get('height'), weight, prog, calories))
        # Log to metrics for chart trend
        from datetime import date
        conn.execute("INSERT INTO metrics (client_name, date, weight) VALUES (?,?,?)", (name, date.today().isoformat(), weight))
    return jsonify({"status": "success", "calories": calories})

@app.route('/get_analytics/<name>')
def get_analytics(name):
    with get_db() as conn:
        rows = conn.execute("SELECT date, weight FROM metrics WHERE client_name=? ORDER BY date ASC", (name,)).fetchall()
    return jsonify({"dates": [r['date'] for r in rows], "weights": [r['weight'] for r in rows]})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
