from flask import current_app, request, jsonify
from flask_restx import Api, Resource, fields

from . import models
from .app_logic import simulate_attack


api = Api()

api_unit = api.model('Unit', {
    'id': fields.Integer,
    'name': fields.String,
    'toughness': fields.Integer,
    'save': fields.String,
    'weapons': fields.List(fields.Integer),
})

api_weapon = api.model('Weapon', {
    'id': fields.Integer,
    'name': fields.String,
    'weapon_skill': fields.String,
    'strength': fields.Integer,
    'attacks': fields.Integer,
    'armour_penetration': fields.Integer,
    'units': fields.List(fields.Integer),
})


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


@api.route("/units")
class ListUnits(Resource):

    @api.marshal_with(api_unit, as_list=True)
    def get(self):
        with current_app.app_context():
            return [unit.to_table_dict() for unit in models.Unit.query.all()]
