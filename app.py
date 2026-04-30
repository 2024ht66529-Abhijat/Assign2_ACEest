from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = "aceest_secret"
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
    conn = get_db()
    clients = conn.execute("SELECT * FROM clients").fetchall()
    progress = conn.execute("SELECT * FROM progress ORDER BY id DESC LIMIT 10").fetchall()
    return render_template('index.html', clients=clients, progress=progress, programs=PROGRAMS.keys())

@app.route('/add_client', methods=['POST'])
def add_client():
    name = request.form['name']
    age = request.form['age']
    weight = float(request.form['weight'])
    program = request.form['program']
    factor = PROGRAMS.get(program, {"factor": 26})["factor"]
    calories = int(weight * factor)

    conn = get_db()
    existing = conn.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if existing:
        flash("Client already exists!")
        return redirect(url_for('index'))

    conn.execute("""INSERT INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                 (name, age, 0, weight, program, calories, 0, 0))
    conn.commit()
    flash("Client added successfully!")
    return redirect(url_for('index'))

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.get_json()
    try:
        name = data.get('name')
        program = data.get('program')
        weight = float(data.get('weight', 0) or 0)
        factor = PROGRAMS.get(program, {"factor": 26})["factor"]
        calories = int(weight * factor) if weight > 0 else 0

        conn = get_db()
        existing = conn.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
        if existing:
            return jsonify({"status": "error", "message": "Client already exists!", "calories": None}), 400

        conn.execute("""INSERT INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (name, data.get('age', 0), data.get('height', 0), weight, program,
                      calories, data.get('target_weight', 0), data.get('target_adherence', 0)))
        conn.commit()
        return jsonify({"status": "success", "calories": calories})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e), "calories": None}), 400

@app.route('/add_progress', methods=['POST'])
def add_progress():
    client_name = request.form['client_name']
    week = request.form['week']
    adherence = request.form['adherence']

    conn = get_db()
    conn.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?,?,?)",
                 (client_name, week, adherence))
    conn.commit()
    flash("Progress logged successfully!")
    return redirect(url_for('index'))

@app.route('/log_workout', methods=['POST'])
def log_workout():
    data = request.get_json()
    try:
        with get_db() as conn:
            conn.execute("""INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
                            VALUES (?, ?, ?, ?, ?)""",
                         (data['client_name'], data['date'], data['type'], data['duration'], data['notes']))
            workout_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            conn.execute("""INSERT INTO exercises (workout_id, name, sets, reps, weight)
                            VALUES (?, ?, ?, ?, ?)""",
                         (workout_id, data['exercise_name'], data['sets'], data['reps'], data['ex_weight']))
            conn.commit()
        return jsonify({"status": "success", "workout_id": workout_id})
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
