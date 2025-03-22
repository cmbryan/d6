from flask import Flask
from .app import api
from . import models
from .models import al, db


def create_app(*args, **kwargs):
    app = Flask(__name__)
    api.init_app(app)
    app.config["SWAGGER"] = {"title": "My API", "uiversion": 3}

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_data.db"  # TODO update for production
    db.init_app(app)
    al.init_app(app)

    with app.app_context():
        db.create_all()
        al.upgrade()

        try:
            # Initial data
            new_unit = models.Unit(name="Skeleton", toughness=5, save="4+")
            existing_unit = db.session.query(models.Unit).filter_by(name=new_unit.name).first()
            if existing_unit:
                db.session.delete(existing_unit)
                db.session.commit()
            db.session.add(new_unit)
            db.session.commit()

            new_weapon = models.Weapon(name="Sword", weapon_skill="3+", strength=4, attacks=5, units=[new_unit])
            existing_weapon = db.session.query(models.Weapon).filter_by(name="Sword").first()
            if existing_weapon:
                db.session.delete(existing_weapon)
                db.session.commit()
            db.session.add(new_weapon)
            db.session.commit()

        except Exception as e:  # Generic exception handling to accomodate sqlite3 and postgres
            db.session.rollback()
            print(f"Constraint error: {e}")

    return app
