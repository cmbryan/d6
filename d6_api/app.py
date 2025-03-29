from flask import Blueprint, current_app, render_template, request, jsonify
from flask_restx import Api, Resource, fields

from d6_api.app_logic import inflict_damage, roll_to_hit, roll_to_save, roll_to_wound

from . import models

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


@api.route("/roll-to-hit")
@api.doc(params={
    'attacker_id': 'ID of attacker',
    'unit_size': {'type': 'integer', 'description': 'Number of models in attacking unit'},
    'defender_id': 'ID of defender',
    'weapon_id': 'ID of weapon used',
})
class RollToHit(Resource):
    def get(self):
        result = roll_to_hit(
            request.args.get("attacker_id"),
            request.args.get("unit_size", 1, type=int),
            request.args.get("defender_id"),
            request.args.get("weapon_id"),
        )
        return jsonify(result)


@api.route("/roll-to-wound")
@api.doc(params={
    'attacker_id': 'ID of attacker',
    'num_attacks': 'Number of attacks',
    'defender_id': 'ID of defender',
    'weapon_id': 'ID of weapon used',
})
class RollToWound(Resource):
    def get(self):
        result = roll_to_wound(
            request.args.get("attacker_id"),
            request.args.get("num_attacks", 1),
            request.args.get("defender_id"),
            request.args.get("weapon_id"),
        )
        return jsonify(result)


@api.route("/roll-to-save")
@api.doc(params={
    'num_wounds': 'Number of wounds',
    'defender_id': 'ID of defender',
    'weapon_id': 'ID of weapon used',
})
class RollToSave(Resource):
    def get(self):
        result = roll_to_save(
            request.args.get("num_wounds", 1),
            request.args.get("defender_id"),
            request.args.get("weapon_id"),
        )
        return jsonify(result)


@api.route("/inflict-damage")
@api.doc(params={
    'num_unsaved_wounds': 'Unsaved wounds',
    'weapon_id': 'ID of weapon used',
})
class InflictDamage(Resource):
    def get(self):
        result = inflict_damage(
            request.args.get("num_unsaved_wounds", 1),
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