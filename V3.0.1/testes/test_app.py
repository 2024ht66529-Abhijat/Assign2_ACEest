import pytest
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    init_db()
    with app.test_client() as client:
        yield client

def test_calorie_logic(client):
    rv = client.post('/save_client', json={
        "name": "Arjun", "weight": 80, "program": "Muscle Gain (MG) – PPL"
    })
    assert rv.get_json()['calories'] == 2800 # 80kg * 35 factor
