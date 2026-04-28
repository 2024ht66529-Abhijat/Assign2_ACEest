from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

PROGRAM_DATA = {
    "Fat Loss (FL)": {
        "workout": "Mon: 5x5 Back Squat + AMRAP\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: 10RFT Deadlifts/Box Jumps\nFri: 30min Active Recovery",
        "diet": "B: 3 Egg Whites + Oats Idli\nL: Grilled Chicken + Brown Rice\nD: Fish Curry + Millet Roti\nTarget: 2,000 kcal",
        "color": "#e74c3c"
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "B: 4 Eggs + PB Oats\nL: Chicken Biryani (250g Chicken)\nD: Mutton Curry + Jeera Rice\nTarget: 3,200 kcal",
        "color": "#2ecc71"
    },
    "Beginner (BG)": {
        "workout": "Circuit Training: Air Squats, Ring Rows, Push-ups.\nFocus: Technique Mastery & Form (90% Threshold)",
        "diet": "Balanced Tamil Meals: Idli-Sambar, Rice-Dal, Chapati.\nProtein: 120g/day",
        "color": "#3498db"
    }
}

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAM_DATA)

@app.route('/get_plan/<program_name>')
def get_plan(program_name):
    plan = PROGRAM_DATA.get(program_name)
    if plan:
        return jsonify(plan)
    return jsonify({"error": "Plan not found"}), 404

# ✅ New Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # For demo purposes, accept any non-empty credentials
        if username and password:
            return jsonify({"message": f"Welcome, {username}!"})
        return jsonify({"error": "Invalid credentials"}), 401
    # For GET requests, return a simple HTML login form
    return '''
        <form method="post">
            <label>Username:</label><input type="text" name="username"><br>
            <label>Password:</label><input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
