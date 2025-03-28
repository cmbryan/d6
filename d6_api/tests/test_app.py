import pytest


@pytest.mark.usefixtures("client")
def test_landing(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "API" in resp.text


@pytest.mark.usefixtures("client")
def test_list_units(client):
    resp = client.get("/units")
    assert resp.status_code == 200
    assert resp.json == [{'id': 1, 'name': 'Captain in Terminator Armour', 'toughness': 5, 'save': '2+', 'weapons': [1, 2, 3, 4]}]
