from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import sqlite3
import random
import io
from fpdf import FPDF
from datetime import datetime

app = Flask(__name__)
app.secret_key = "aceest_ultra_secret_key"
DB_NAME = "aceest_fitness.db"

PROGRAMS = {
    "Fat Loss (FL) – 3 day": {"factor": 22},
    "Fat Loss (FL) – 5 day": {"factor": 24},
    "Muscle Gain (MG) – PPL": {"factor": 35},
    "Beginner (BG)": {"factor": 26},
}

EXERCISES_POOL = {
    "Strength": ["Squat", "Deadlift", "Bench Press", "Overhead Press"],
    "Hypertrophy": ["Leg Press", "Lat Pulldown", "Bicep Curl", "Tricep Extension"],
    "Conditioning": ["Running", "Cycling", "Rowing", "Burpees"],
    "Full Body": ["Push-Up", "Pull-Up", "Lunge", "Plank"]
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)")
        conn.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('admin','admin','Admin')")
        conn.execute("""CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, age INTEGER, height REAL, weight REAL, 
            program TEXT, calories INTEGER, membership_expiry TEXT)""")

@app.route('/')
def index():
    if 'user' not in session: return redirect(url_for('login'))
    with get_db() as conn:
        clients = conn.execute("SELECT name FROM clients").fetchall()
    return render_template('dashboard.html', programs=PROGRAMS, clients=clients, role=session['role'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pw = request.form['password']
        with get_db() as conn:
            row = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pw)).fetchone()
            if row:
                session['user'], session['role'] = row['username'], row['role']
                return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    factor = PROGRAMS.get(data['program'], {'factor': 25})['factor']
    calories = int(float(data['weight']) * factor) if float(data['weight']) > 0 else 0
    with get_db() as conn:
        conn.execute("INSERT OR REPLACE INTO clients (name, age, height, weight, program, calories, membership_expiry) VALUES (?,?,?,?,?,?,?)",
                     (data['name'], data['age'], data['height'], data['weight'], data['program'], calories, data['membership']))
    return jsonify({"status": "success", "calories": calories})

@app.route('/generate_ai', methods=['POST'])
def generate_ai():
    data = request.json
    level = data['level'].lower()
    config = {"beginner": {"sets": (2,3), "days": 3}, "intermediate": {"sets": (3,4), "days": 4}, "advanced": {"sets": (4,5), "days": 5}}.get(level)
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"][:config['days']]
    prog = []
    for d in days:
        exs = random.sample(EXERCISES_POOL["Full Body"], k=3)
        for e in exs:
            prog.append({"day": d, "exercise": e, "sets": random.randint(*config['sets']), "reps": random.randint(8, 12)})
    return jsonify(prog)

@app.route('/export_pdf/<name>')
def export_pdf(name):
    with get_db() as conn:
        row = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Client Report - {row['name']}", ln=True, align="C")
    pdf.output(dest='S').encode('latin-1')
    return send_file(io.BytesIO(pdf.output(dest='S').encode('latin-1')), mimetype='application/pdf', as_attachment=True, download_name=f"{name}.pdf")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
