from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

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
            id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, week TEXT, adherence INTEGER)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, 
            workout_type TEXT, duration_min INTEGER, notes TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT, workout_id INTEGER, 
            name TEXT, sets INTEGER, reps INTEGER, weight REAL)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT, date TEXT, 
            weight REAL, waist REAL, bodyfat REAL)""")

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAMS)

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    try:
        name = data.get('name')
        program = data.get('program')
        weight = float(data.get('weight', 0) or 0)
        factor = PROGRAMS[program]['factor']
        calories = int(weight * factor) if weight > 0 else 0
        with get_db() as conn:
            conn.execute("""INSERT OR REPLACE INTO clients 
                (name, age, height, weight, program, calories, target_weight, target_adherence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (name, data.get('age', 0), data.get('height', 0), weight, program, 
                 calories, data.get('target_weight', 0), data.get('target_adherence', 0)))
        return jsonify({"status": "success", "calories": calories})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/workout_history/<name>')
def workout_history(name):
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM workouts WHERE client_name=? ORDER BY date DESC", (name,)).fetchall()
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
