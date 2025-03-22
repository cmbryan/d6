from flask import current_app, request, jsonify
from flask_restx import Api, Resource

from . import models
from .app_logic import simulate_attack


api = Api()

@api.route("/attack")
@api.doc(params={'id': 'An ID'})
class Attack(Resource):
    def get(self):
        assert request.args.get("attacker"), "Attacker is required."
        assert request.args.get("defender"), "Defender is required."
        assert request.args.get("weapon"), "Weapon is required."

        result = simulate_attack(
            request.args.get("attacker"),
            request.args.get("attack_unit_size", 1),
            request.args.get("defender"),
            request.args.get("weapon"),
        )
        return jsonify(result)


class ListUnits(Resource):
    def get(self):
        with current_app.app_context():
            units = [unit.to_table_dict() for unit in models.Unit.query.all()]
        return jsonify(units)
