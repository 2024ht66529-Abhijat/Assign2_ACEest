import pytest
import sqlite3
from app import app, DB_NAME

@pytest.fixture
def client():
    """Configures the app for testing and provides a test client."""
    app.config['TESTING'] = True
    # We use the app's existing DB logic but ensure it's initialized
    with app.test_client() as client:
        with app.app_context():
            # Setup: Ensure tables exist before each test
            conn = sqlite3.connect(DB_NAME)
            conn.execute("DELETE FROM clients") # Clear old test data
            conn.execute("DELETE FROM progress")
            conn.commit()
            conn.close()
        yield client

def test_index_page_loads(client):
    """Verify the home page loads with the correct title."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"ACEest Functional Fitness System" in response.data

def test_add_client_calculation(client):
    """Verify client addition and the calorie formula (Weight * Factor)."""
    # Program: Muscle Gain (MG) has a factor of 35. 
    # 80kg * 35 = 2800 calories.
    data = {
        'name': 'John Doe',
        'age': '25',
        'weight': '80',
        'program': 'Muscle Gain (MG)'
    }
    response = client.post('/add_client', data=data, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"John Doe" in response.data
    assert b"2800" in response.data  # Checking the calculated calories

def test_duplicate_client_error(client):
    """Verify that adding the same client name triggers the integrity flash."""
    data = {'name': 'Unique User', 'age': '30', 'weight': '70', 'program': 'Beginner (BG)'}
    client.post('/add_client', data=data)
    
    # Try adding again
    response = client.post('/add_client', data=data, follow_redirects=True)
    assert b"Client already exists!" in response.data

def test_add_progress_log(client):
    """Verify that progress logs are saved and displayed."""
    data = {
        'client_name': 'John Doe',
        'week': 'Week 1',
        'adherence': '95'
    }
    response = client.post('/add_progress', data=data, follow_redirects=True)
    
    assert response.status_code == 200
    assert b"Week 1" in response.data
    assert b"95%" in response.data
