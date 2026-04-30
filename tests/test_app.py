import pytest
import sqlite3
import os
from app import app, DB_NAME

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Ensure a fresh DB for testing
    if os.path.exists(DB_NAME): os.remove(DB_NAME)
    from app import init_db
    init_db()
    
    with app.test_client() as client:
        yield client

def test_save_and_load_client(client):
    """Test calorie calculation: 100kg * Muscle Gain (35) = 3500."""
    client.post('/save_client', json={
        "name": "Arjun", "age": 25, "weight": 100, "program": "Muscle Gain (MG)"
    })
    
    rv = client.get('/load_client/Arjun')
    data = rv.get_json()
    assert data['calories'] == 3500

def test_progress_data_retrieval(client):
    """Test saving and retrieving progress for charting."""
    client.post('/save_progress', json={"name": "Arjun", "adherence": 85})
    
    rv = client.get('/get_progress/Arjun')
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['adherence'] == 85
