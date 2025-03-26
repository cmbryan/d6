from flask import Flask

from d6_api.util import create_db
from .app import api
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
            create_db(app)

        except Exception as e:  # Generic exception handling to accomodate sqlite3 and postgres
            db.session.rollback()
            print(f"Constraint error: {e}")

    return app
