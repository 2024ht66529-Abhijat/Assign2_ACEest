import pytest
import os
from app import app, init_db, DB_NAME

@pytest.fixture
def client():
    # Setup: use a temporary test database
    app.config['TESTING'] = True
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
    init_db()
    
    with app.test_client() as client:
        yield client
        
    # Teardown: clean up
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)