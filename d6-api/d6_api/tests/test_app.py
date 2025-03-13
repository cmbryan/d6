import pytest
from d6_api import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_landing(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert "API" in resp.text


def test_list_units(client):
    resp = client.get('/list_units')
    assert resp.status_code == 200
    assert resp.json == ["Skeleton"]