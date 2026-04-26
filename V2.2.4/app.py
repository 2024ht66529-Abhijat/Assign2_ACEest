from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

# Core Program Data
PROGRAMS = {
    "Fat Loss (FL) – 3 day": {"factor": 22, "desc": "3-day full-body fat loss"},
    "Fat Loss (FL) – 5 day": {"factor": 24, "desc": "5-day split, higher volume fat loss"},
    "Muscle Gain (MG) – PPL": {"factor": 35, "desc": "Push/Pull/Legs hypertrophy"},
    "Beginner (BG)": {"factor": 26, "desc": "3-day simple beginner full-body"},
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE,
            age INTEGER, height REAL, weight REAL, program TEXT,
            calories INTEGER, target_weight REAL, target_adherence INTEGER)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, 
            week TEXT, adherence INTEGER)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT,
            date TEXT, weight REAL, waist REAL, bodyfat REAL)""")

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAMS)

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    try:
        # Use .get() to avoid KeyError if fields are empty
        name = data.get('name')
        program = data.get('program')
        weight = float(data.get('weight', 0) or 0)
        
        if not name or not program:
            return jsonify({"status": "error", "message": "Name and Program are required"}), 400

        factor = PROGRAMS[program]['factor']
        calories = int(weight * factor) if weight > 0 else 0

        with get_db() as conn:
            conn.execute("""INSERT OR REPLACE INTO clients 
                (name, age, height, weight, program, calories, target_weight, target_adherence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, 
                 int(data.get('age', 0) or 0), 
                 float(data.get('height', 0) or 0), 
                 weight, 
                 program, 
                 calories, 
                 float(data.get('target_weight', 0) or 0), 
                 int(data.get('target_adherence', 0) or 0)))
        return jsonify({"status": "success", "calories": calories})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_summary/<name>')
def get_summary(name):
    with get_db() as conn:
        client = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
        if not client:
            return jsonify({"error": "Not Found"}), 404
        
        stats = conn.execute("SELECT COUNT(*), AVG(adherence) FROM progress WHERE client_name=?", (name,)).fetchone()
        metric = conn.execute("SELECT * FROM metrics WHERE client_name=? ORDER BY date DESC LIMIT 1", (name,)).fetchone()
        
        c_dict = dict(client)
        return jsonify({
            "profile": c_dict,
            "prog_desc": PROGRAMS.get(c_dict['program'], {}).get("desc", ""),
            "weeks": stats[0],
            "avg_adh": round(stats[1], 1) if stats[1] else 0,
            "last_metric": dict(metric) if metric else None
        })

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
