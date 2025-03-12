from flask import request, jsonify
from flask_restx import Api, Resource
from flasgger import swag_from

from .app_logic import units, weapons, simulate_attack




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


api = Api()
api.add_resource(Attack, "/attack")
api.add_resource(Attack, "/")
