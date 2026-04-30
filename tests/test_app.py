import pytest
import os
import io
import sqlite3
from app import app, init_db, DB_NAME, get_db

@pytest.fixture
def client():
    """Configures the app for testing and provides a clean database."""
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test_secret'
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
    with app.test_client() as client:
        yield client

def test_login_and_session(client):
    """Verify valid admin credentials."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'admin'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"ACEest Analytics Dashboard" in response.data

def test_unauthorized_redirect(client):
    """Verify unauthorized access redirect."""
    response = client.get('/', follow_redirects=True)
    assert b"LOGIN" in response.data

def test_save_client_and_calorie_calc(client):
    """Verify client saving and calorie logic."""
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    payload = {
        "name": "Arjun",
        "age": 28,
        "height": 175.5,
        "weight": 80.0,
        "program": "Muscle Gain (MG) – PPL",
        "membership": "2025-12-31"
    }
    response = client.post('/save_client', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert data['calories'] == 2800

def test_ai_program_generation_logic(client):
    """Verify AI generates correct days."""
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    client.post('/save_client', json={
        "name": "BeginnerBot",
        "weight": 70,
        "program": "Beginner (BG)",
        "age": 20,
        "height": 160,
        "membership": ""
    })
    res_beg = client.post('/generate_ai', json={"name": "BeginnerBot", "level": "beginner"})
    days_beg = set(item['day'] for item in res_beg.get_json())
    assert len(days_beg) == 3

def test_pdf_export_stream(client):
    """Verify PDF export."""
    client.post('/login', data={'username': 'admin', 'password': 'admin'})
    client.post('/save_client', json={
        "name": "ExportUser",
        "weight": 75,
        "program": "Beginner (BG)",
        "age": 30,
        "height": 170,
        "membership": "2024-01-01"
    })
    response = client.get('/export_pdf/ExportUser')
    assert response.status_code == 200
    assert response.data.startswith(b'%PDF')

def test_invalid_login(client):
    """Verify wrong credentials."""
    response = client.post('/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"LOGIN" in response.data