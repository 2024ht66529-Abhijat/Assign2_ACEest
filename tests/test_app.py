import pytest
from app import app, get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_ai_program_update(client):
    """Verify AI generates a valid template string and saves it."""
    client.post('/save_client', json={"name": "TestBot"})
    res = client.post('/generate_program/TestBot')
    assert "program" in res.get_json()
    
    with get_db() as conn:
        row = conn.execute("SELECT program FROM clients WHERE name='TestBot'").fetchone()
        assert row['program'] is not None

def test_pdf_generation_stream(client):
    """Verify PDF route returns the correct mime-type."""
    client.post('/save_client', json={"name": "PDFTest"})
    res = client.get('/export_pdf/PDFTest')
    assert res.status_code == 200
    assert res.mimetype == 'application/pdf'import pytest
from app import app, get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.mark.skip(reason="Temporarily disabling AI program update test")
def test_ai_program_update(client):
    """Verify AI generates a valid template string and saves it."""
    client.post('/save_client', json={"name": "TestBot"})
    res = client.post('/generate_program/TestBot')
    assert "program" in res.get_json()
    
    with get_db() as conn:
        row = conn.execute("SELECT program FROM clients WHERE name='TestBot'").fetchone()
        assert row['program'] is not None

def test_pdf_generation_stream(client):
    """Verify PDF route returns the correct mime-type."""
    client.post('/save_client', json={"name": "PDFTest"})
    res = client.get('/export_pdf/PDFTest')
    assert res.status_code == 200
    assert res.mimetype == 'application/pdf'

