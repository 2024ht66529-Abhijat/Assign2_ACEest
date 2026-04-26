import pytest
from app import app, init_db, DB_NAME
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    if os.path.exists(DB_NAME): os.remove(DB_NAME)
    init_db()
    with app.test_client() as client:
        yield client

def test_calorie_calculation(client):
    rv = client.post('/save_client', json={
        "name": "Arjun", "weight": 80, "program": "Muscle Gain (MG) – PPL"
    })
    assert rv.status_code == 200
    assert rv.get_json()['calories'] == 2800 # 80kg * 35 factor
