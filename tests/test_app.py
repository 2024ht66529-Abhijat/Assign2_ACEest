import pytest

def test_calorie_logic(client):
  
    rv = client.post('/save_client', json={
        "name": "Arjun",
        "weight": 80,
        "program": "Muscle Gain (MG) – PPL"
    })
    
    data = rv.get_json()
    
    # Debugging 
    assert data is not None, "Response body was empty"
    assert data.get('calories') == 2800, f"Expected 2800, but got {data.get('calories')}. Error: {data.get('message')}"
