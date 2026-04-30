import pytest
from app import app, get_db, DB_NAME
def test_workout_exercise_linking(client):
    payload = {
        "client_name": "Arjun",
        "date": "2023-10-26",
        "type": "Strength",
        "duration": 60,
        "notes": "Testing links",
        "exercise_name": "Squat",
        "sets": 3, "reps": 5, "ex_weight": 100
    }
    client.post('/log_workout', json=payload)
    
    with get_db() as conn:
        workout = conn.execute("SELECT id FROM workouts").fetchone()
        exercise = conn.execute("SELECT * FROM exercises WHERE workout_id=?", (workout['id'],)).fetchone()
        assert exercise['name'] == "Squat"
        assert exercise['weight'] == 100
