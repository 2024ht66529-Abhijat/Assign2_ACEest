from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Data combined from your latest Tkinter update
PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: Back Squat 5x5 + Core\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: Deadlift + Box Jumps\nFri: Zone 2 Cardio 30min",
        "diet": "Breakfast: Egg Whites + Oats\nLunch: Grilled Chicken + Brown Rice\nDinner: Fish Curry + Millet Roti\nTarget: ~2000 kcal",
        "color": "#e74c3c",
        "calorie_factor": 22
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "Breakfast: Eggs + Peanut Butter Oats\nLunch: Chicken Biryani\nDinner: Mutton Curry + Rice\nTarget: ~3200 kcal",
        "color": "#2ecc71",
        "calorie_factor": 35
    },
    "Beginner (BG)": {
        "workout": "Full Body Circuit:\n- Air Squats\n- Ring Rows\n- Push-ups\nFocus: Technique & Consistency",
        "diet": "Balanced Tamil Meals\nIdli / Dosa / Rice + Dal\nProtein Target: 120g/day",
        "color": "#3498db",
        "calorie_factor": 26
    }
}

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAMS)

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    program_key = data.get('program')
    weight = float(data.get('weight', 0))
    
    program = PROGRAMS.get(program_key)
    if not program:
        return jsonify({"error": "Invalid program"}), 400
    
    # Matching your self.weight_var.get() * data["calorie_factor"] logic
    calories = int(weight * program['calorie_factor']) if weight > 0 else "--"
    
    return jsonify({
        "workout": program['workout'],
        "diet": program['diet'],
        "color": program['color'],
        "calories": calories
    })

if __name__ == '__main__':
    app.run(debug=True)
