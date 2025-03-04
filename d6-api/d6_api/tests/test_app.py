import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_landing(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.text == 'Hello, World!'