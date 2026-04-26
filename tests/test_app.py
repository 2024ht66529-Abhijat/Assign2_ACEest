import pytest
import os
import sys

# Ensure the root directory is in the path so we can import app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_dashboard_header_exists(client):
    """Check if the Tamil Nadu Context header exists on the main page."""
    response = client.get('/')
    assert response.status_code == 200
    # Verifies the static label in your HTML
    assert b"Daily Nutrition Plan (Tamil Nadu Context)" in response.data

def test_beginner_diet_tamil_context(client):
    """Verify that the Beginner (BG) plan returns Tamil-specific diet items."""
    # We encode the URL to handle spaces: Beginner (BG) -> Beginner%20(BG)
    response = client.get('/get_plan/Beginner%20(BG)')
    assert response.status_code == 200
    
    data = response.get_json()
    # Check for specific Tamil context keywords from your setup_data
    assert "Balanced Tamil Meals" in data['diet']
    assert "Idli-Sambar" in data['diet']
    assert "Rice-Dal" in data['diet']

def test_muscle_gain_diet_tamil_context(client):
    """Verify that the Muscle Gain (MG) plan returns Tamil-specific diet items."""
    response = client.get('/get_plan/Muscle%20Gain%20(MG)')
    assert response.status_code == 200
    
    data = response.get_json()
    # Check for specific non-veg Tamil context keywords
    assert "Chicken Biryani" in data['diet']
    assert "Mutton Curry" in data['diet']
    assert "Jeera Rice" in data['diet']
