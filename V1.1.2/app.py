from flask import Flask, render_template, request, jsonify, Response
import csv
import io

app = Flask(__name__)

# Core Data
PROGRAMS = {
    "Fat Loss (FL)": {"workout": "Back Squat, Cardio, Bench, Deadlift, Recovery", "diet": "Egg Whites, Chicken, Fish Curry", "color": "#e74c3c", "calorie_factor": 22},
    "Muscle Gain (MG)": {"workout": "Squat, Bench, Deadlift, Press, Rows", "diet": "Eggs, Biryani, Mutton Curry", "color": "#2ecc71", "calorie_factor": 35},
    "Beginner (BG)": {"workout": "Air Squats, Ring Rows, Push-ups", "diet": "Balanced Tamil Meals", "color": "#3498db", "calorie_factor": 26}
}

# In-memory store matching your Tkinter self.clients
clients_list = []

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAMS)

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    # Calorie calculation logic
    program = PROGRAMS.get(data['program'])
    weight = float(data.get('weight', 0))
    calories = int(weight * program['calorie_factor']) if weight > 0 else 0
    
    client_entry = {
        "name": data['name'],
        "age": data['age'],
        "weight": weight,
        "program": data['program'],
        "adherence": int(data['adherence']),
        "notes": data['notes'],
        "calories": calories,
        "color": program['color'],
        "workout": program['workout'],
        "diet": program['diet']
    }
    clients_list.append(client_entry)
    return jsonify({"status": "success", "clients": clients_list})

@app.route('/export_csv')
def export_csv():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Age", "Weight", "Program", "Adherence", "Notes"])
    for c in clients_list:
        writer.writerow([c['name'], c['age'], c['weight'], c['program'], c['adherence'], c['notes']])
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=clients.csv"}
    )

if __name__ == '__main__':
    app.run(debug=True)
