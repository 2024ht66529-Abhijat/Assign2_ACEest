import pytest
import sqlite3
from app import app, DB_NAME

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        # Clear DB before each test
        conn = sqlite3.connect(DB_NAME)
        conn.execute("DELETE FROM clients")
        conn.execute("DELETE FROM progress")
        conn.commit()
        conn.close()
        yield client

def test_save_and_load_client(client):
    """Test saving a client and immediately loading them back."""
    payload = {"name": "Arjun", "age": 25, "weight": 70, "program": "Muscle Gain (MG)"}
    client.post('/save_client', json=payload)
    
    response = client.get('/load_client/Arjun')
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['calories'] == 2450  # 70 * 35

def test_save_progress(client):
    """Test progress logging."""
    payload = {"name": "Arjun", "adherence": 90}
    response = client.post('/save_progress', json=payload)
    assert response.status_code == 200
    assert "Progress logged" in response.get_json()['message']
