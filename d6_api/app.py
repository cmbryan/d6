from flask import Blueprint, current_app, render_template, request, jsonify
from flask_restx import Api, Resource, fields

from . import models
from .app_logic import simulate_attack

bp = Blueprint('api', __name__)

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
@api.doc(params={
    'attacker_id': 'ID of attacker',
    'defender_id': 'ID of defender',
    'weapon_id': 'ID of weapon used',
})
class Attack(Resource):
    def get(self):
        result = simulate_attack(
            request.args.get("attacker_id"),
            request.args.get("attack_unit_size", 1),
            request.args.get("defender_id"),
            request.args.get("weapon_id"),
        )
        return jsonify(result)


@api.route("/units")
class ListUnits(Resource):

    @api.marshal_with(api_unit, as_list=True)
    def get(self):
        with current_app.app_context():
            return [unit.serialize() for unit in models.Unit.query.all()]


@api.route("/weapons")
class ListWeapons(Resource):

    @api.marshal_with(api_weapon, as_list=True)
    def get(self):
        with current_app.app_context():
            return [weapon.serialize() for weapon in models.Weapon.query.all()]


@bp.route("/play")
def play():
    return render_template("play.html")