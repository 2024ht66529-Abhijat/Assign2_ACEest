from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "aceest_secret"
DB_NAME = "aceest_fitness.db"

# --- Program Factors from your Tkinter code ---
PROGRAMS = {
    "Fat Loss (FL)": 22,
    "Muscle Gain (MG)": 35,
    "Beginner (BG)": 26
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE, age INTEGER, weight REAL,
                program TEXT, calories INTEGER
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT, week TEXT, adherence INTEGER
            )""")

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
    
    # Matching your Tkinter calorie calculation factor
    calories = int(weight * PROGRAMS.get(program, 26))
    
    conn = get_db()
    # Check for duplicate before insert
    existing = conn.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if existing:
        flash("Client already exists!")
        return redirect(url_for('index'))

    conn.execute("INSERT INTO clients (name, age, weight, program, calories) VALUES (?,?,?,?,?)",
                 (name, age, weight, program, calories))
    conn.commit()
    flash("Client added successfully!")
    return redirect(url_for('index'))

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

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
