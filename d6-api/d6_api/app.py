from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flasgger import Swagger, swag_from

from app_logic import units, weapons, simulate_attack


app = Flask(__name__)
api = Api(app)
app.config["SWAGGER"] = {"title": "My API", "uiversion": 3}
swagger = Swagger(app)


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
                    "description": "The attacker\s weapon",
                },
            ],
            "responses": {
                200: {
                    "description": "The amount of damage resulting from the attack.",
                    "type": "integer",
                }
            },
        }
    )
    def get(self):
        result = simulate_attack(
            request.args.get("attacker"),
            request.args.get("defender"),
            request.args.get("weapon"),
        )
        return jsonify(result)


api.add_resource(Attack, "/attack")


@app.route("/")
def hello_world():
    return "Hello, World!"


if __name__ == "__main__":
    app.run(debug=True)
