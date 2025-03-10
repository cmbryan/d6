from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flasgger import Swagger, swag_from
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

from app_logic import units, weapons, simulate_attack

class Base(DeclarativeBase):
  pass

app = Flask(__name__)
api = Api(app)
app.config["SWAGGER"] = {"title": "My API", "uiversion": 3}
swagger = Swagger(app)

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test_data.db"  # TODO update for production
db.init_app(app)


class Attack(Resource):
    @swag_from(
        {
            "parameters": [
                {
                    "name": "attacker",
                    "in": "query",
                    "type": "string",
                    "enum": units,
                    "required": True,
                    "description": "The attacking unit",
                },
                {
                    "name": "attack_unit_size",
                    "in": "query",
                    "type": "int",
                    "required": True,
                    "description": "Number of models in the attacking unit",
                },
                {
                    "name": "defender",
                    "in": "query",
                    "type": "string",
                    "enum": units,
                    "required": True,
                    "description": "The defending unit",
                },
                {
                    "name": "weapon",
                    "in": "query",
                    "type": "string",
                    "enum": weapons,
                    "required": True,
                    "description": "The attacker's weapon",
                },
            ],
            "responses": {
                200: {
                    "description": "The result of the attack simulation.",
                    "content": {
                        "application/json": {
                            "examples": {
                                "example1": {
                                    "summary": "Successful response",
                                    "value": {
                                        "log": [
                                            "Attacker rolled for random attacks...",
                                            "Attacker attacks X times...",
                                            "X attacks were successful...",
                                            "Weapon requires Y+ to wound...",
                                            "Z attacks were wounding...",
                                            "Defender requires W+ to save...",
                                            "V wounds were saved..."
                                        ],
                                        "damage": 10
                                    }
                                }
                            }
                        }
                    }
                }
            },
        }
    )
    def get(self):
        result = simulate_attack(
            request.args.get("attacker"),
            request.args.get("attack_unit_size"),
            request.args.get("defender"),
            request.args.get("weapon"),
        )
        return jsonify(result)


api.add_resource(Attack, "/attack")


if __name__ == "__main__":
    app.run(debug=True)
