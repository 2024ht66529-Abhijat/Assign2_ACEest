import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_calorie_calculation_logic(client):
    """Verify Weight (100kg) * MG Factor (35) = 3500 kcal."""
    payload = {"program": "Muscle Gain (MG)", "weight": 100}
    response = client.post('/calculate', json=payload)
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['calories'] == 3500
    assert "Chicken Biryani" in data['diet']

def test_empty_weight_handling(client):
    """Ensure app handles zero weight gracefully."""
    payload = {"program": "Beginner (BG)", "weight": 0}
    response = client.post('/calculate', json=payload)
    assert response.get_json()['calories'] == "--"

def test_workout_color_assignment(client):
    """Check if Fat Loss returns the correct e74c3c hex code."""
    payload = {"program": "Fat Loss (FL)", "weight": 70}
    response = client.post('/calculate', json=payload)
    assert response.get_json()['color'] == "#e74c3c"
