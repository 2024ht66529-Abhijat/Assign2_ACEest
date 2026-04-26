from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss (FL)": {"factor": 22},
    "Muscle Gain (MG)": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE,
            age INTEGER, weight REAL, program TEXT, calories INTEGER)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT, client_name TEXT,
            week TEXT, adherence INTEGER)""")

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAMS.keys())

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    factor = PROGRAMS[data['program']]['factor']
    calories = int(float(data['weight']) * factor)
    
    try:
        with get_db() as conn:
            conn.execute("""INSERT OR REPLACE INTO clients 
                (name, age, weight, program, calories) VALUES (?, ?, ?, ?, ?)""",
                (data['name'], data['age'], data['weight'], data['program'], calories))
        return jsonify({"status": "success", "message": "Client data saved"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/load_client/<name>')
def load_client(name):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    if row:
        return jsonify(dict(row))
    return jsonify({"status": "error", "message": "Client not found"}), 404

@app.route('/save_progress', methods=['POST'])
def save_progress():
    data = request.json
    week = datetime.now().strftime("Week %U - %Y")
    with get_db() as conn:
        conn.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
                    (data['name'], week, data['adherence']))
    return jsonify({"status": "success", "message": f"Progress logged for {week}"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
