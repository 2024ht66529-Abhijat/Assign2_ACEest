import pytest
from app import app, init_db

@pytest.fixture
def client():
    # Ensure database tables exist before tests
    init_db()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
