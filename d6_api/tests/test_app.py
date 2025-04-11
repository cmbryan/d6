import pytest

from d6_api.app import Category


@pytest.mark.usefixtures("client")
def test_landing(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert "API" in resp.text


@pytest.mark.usefixtures("populated_db")
def test_list_units(populated_db):
    resp = populated_db.get("/units")
    assert resp.status_code == 200
    assert resp.json == [
        {'id': 1, 'name': 'Captain in Terminator Armour', 'toughness': 5, 'save': '2+', 'weapons': [1, 2]},
        {'id': 2, 'name': 'Psychophage', 'toughness': 9, 'save': '4+', 'weapons': [3]},
    ]


@pytest.mark.usefixtures("populated_db")
def test_list_weapons(populated_db):
    resp = populated_db.get("/weapons")
    assert resp.status_code == 200
    assert resp.json == [
        {'id': 1, 'name': 'Storm bolter', 'weapon_skill': '3+', 'strength': 4, 'attacks': '2', 'armour_penetration': 0, 'units': [1]},
        {'id': 2, 'name': 'Chainsword', 'weapon_skill': '3+', 'strength': 3, 'attacks': '1', 'armour_penetration': -1, 'units': [1]},
        {'id': 3, 'name': 'Talons', 'weapon_skill': '4+', 'strength': 1, 'attacks': 'D6+3', 'armour_penetration': 0, 'units': [2]},
    ]


@pytest.mark.usefixtures("client")
def test_add_unit(client):
    # First add a weapon
    resp = client.post("/add-weapon", json={
        "name": "Test Weapon",
        "weapon_skill": "1+",
        "strength": "1",
        "attacks": "1",
        "armour_penetration": "0",
    })
    assert resp.status_code == 200
    weapon_id = resp.json["id"]

    # Then, add a unit bearing that weapon
    resp = client.post("/add-unit", json={
        "name": "Test Unit",
        "category": Category.STARTER_KIT_40K,
        "toughness": "1",
        "save": "1+",
        "weapon_ids": [weapon_id]
    })
    assert resp.status_code == 200
    assert resp.json == {
        'id': 1,
        'category': 'Warhammer 40k starter kit, 10th edition',
        'invulnerable_save': '',
        'name': 'Test Unit',
        'toughness': 1,
        'save': '1+',
        'weapons': [1],
    }

@pytest.mark.usefixtures("client")
def test_add_weapon(client):
    # First add a unit
    resp = client.post("/add-unit", json={
        "name": "Test Unit",
        "category": Category.STARTER_KIT_40K,
        "toughness": "1",
        "save": "1+",
    })
    assert resp.status_code == 200
    unit_id = resp.json["id"]

    # Then, add a weapon to that unit
    resp = client.post("/add-weapon", json={
        "name": "Test Weapon",
        "weapon_skill": "1+",
        "strength": "1",
        "attacks": "1",
        "armour_penetration": "0",
        "unit_ids": [unit_id]
    })
    assert resp.status_code == 200
    assert resp.json == {
        'id': 1,
        'name': 'Test Weapon',
        'anti_infantry': '',
        'armour_penetration': 0,
        'attacks': '1',
        'damage': 1,
        'devastating_wounds': False,
        'range': 0,
        'rapid_fire': 0,
        'strength': 1,
        'units': [1],
        'weapon_skill': '1+',
    }
