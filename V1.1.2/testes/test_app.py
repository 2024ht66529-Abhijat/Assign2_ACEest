import pytest
from app import app, clients_list

@pytest.fixture
def client():
    clients_list.clear() # Reset list before tests
    with app.test_client() as client:
        yield client

def test_save_client_and_calculation(client):
    """Verify data reaches the list and calories calculate (70kg * 22 for FL)."""
    payload = {
        "name": "Arjun", "age": 28, "weight": 70, 
        "program": "Fat Loss (FL)", "adherence": 85, "notes": "Strong start"
    }
    response = client.post('/save_client', json=payload)
    data = response.get_json()
    
    assert response.status_code == 200
    assert data['clients'][0]['calories'] == 1540
    assert len(clients_list) == 1

def test_csv_export(client):
    """Ensure CSV is generated with the correct headers."""
    client.post('/save_client', json={"name": "Test", "age": 20, "weight": 60, "program": "Beginner (BG)", "adherence": 100, "notes": "N/A"})
    response = client.get('/export_csv')
    
    assert response.status_code == 200
    assert b"Name,Age,Weight,Program,Adherence,Notes" in response.data
    assert b"Test" in response.data
