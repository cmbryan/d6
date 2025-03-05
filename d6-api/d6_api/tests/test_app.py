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


def test_test_resource(client):
    resp = client.get('/test-resource')
    assert resp.status_code == 200
    assert resp.json == {'hello': 'world'}
