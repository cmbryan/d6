import pytest
from d6_api import create_app
from d6_api.models import Unit, Weapon, db


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        with client.application.app_context():
            db.session.query(Unit).delete()
            db.session.query(Weapon).delete()
            db.session.query(unit_weapon_association).delete()
            db.session.commit()

        yield client


@pytest.fixture()
def populated_db(client):
    """
    Populates the database with test data.
    """
    with client.application.app_context():
        # Create some test weapons
        weapon1 = Weapon(name='Storm bolter', weapon_skill='3+', strength=4, attacks='2', armour_penetration=0)
        weapon2 = Weapon(name='Chainsword', weapon_skill='3+', strength=3, attacks='1', armour_penetration=-1)
        weapon3 = Weapon(name='Talons', weapon_skill='4+', strength=1, attacks='D6+3', armour_penetration=0)
        db.session.add_all([weapon1, weapon2])
        db.session.commit()

        # Create some test units
        unit1 = Unit(name='Captain in Terminator Armour', toughness=5, save='2+')
        unit1.weapons.append(weapon1)
        unit1.weapons.append(weapon2)

        unit2 = Unit(name='Psychophage', toughness=9, save='4+')
        unit2.weapons.append(weapon3)

        db.session.add_all([unit1, unit2])
        db.session.commit()

    yield client