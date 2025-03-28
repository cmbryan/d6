from pathlib import Path
import re

from .models import Unit, Weapon, db
from .util import parse_stat, roll_dice, to_int

current_module_dir = Path(__file__).resolve().parent


def simulate_attack(attacker_id: int, attack_unit_size: int, defender_id: int, weapon_id: int):
    """
    Simulates an attack. Currently hard-coded to use the 40k, 10th edition ruleset.

    Args:
        attacker_id (int): The id of the attacking unit.
        attack_unit_size (int): The number of models in the attacking unit.
        defender_id (int): The id of the defending unit.
        weapon_id (int): The id of the weapon used by the attacker.

    Returns:
        dict: A dictionary containing the result of the attack simulation, including the total damage inflicted and a log of actions.
    """

    result = {"log": [], "damage": 0}

    attacker = db.session.get(Unit, attacker_id)
    defender = db.session.get(Unit, defender_id)
    weapon = db.session.get(Weapon, weapon_id)

    assert attacker, f"Attacker id:{attacker_id} not found."
    assert defender, f"Defender id:{defender_id} not found."
    assert weapon in attacker.weapons, f"{attacker.name} does not have a weapon id:{weapon_id}."

    random_attacks = re.match(r"(?P<num_dice>\d+)?D6(\+(?P<modifier>\d+))?", str(weapon.attacks))
    if random_attacks:
        num_dice = (to_int(random_attacks.group("num_dice")) or 1) * attack_unit_size
        modifier = to_int(random_attacks.group("modifier"))
        roll = sum(roll_dice(num_dice))
        attacks = roll + num_dice * modifier
        result["log"].append(f"{attacker.name} x{attack_unit_size} rolled for random attacks ({weapon.attacks}) => {attacks}.")
    else:
        # Normal attacks
        attacks = weapon.attacks * attack_unit_size
    result["log"].append(f"{attacker.name} x{attack_unit_size} with {weapon.name} ({weapon.attacks} attacks) for a total of {attacks} attacks.")

    result["log"].append(f"{weapon.name} requires {parse_stat(weapon.weapon_skill)}+ to hit.")
    hits = roll_dice(attacks, success_threshold=parse_stat(weapon.weapon_skill))
    result["log"].append(f"{hits} => {len(hits)} attacks were successful.")

    if not hits:
        return result

    if weapon.strength >= (defender.toughness * 2):
        success_threshold = 2
    elif weapon.strength > defender.toughness:
        success_threshold = 3
    elif weapon.strength == defender.toughness:
        success_threshold = 4
    elif weapon.strength < defender.toughness:
        success_threshold = 5
    elif weapon.strength <= (defender.toughness / 2):
        success_threshold = 6
    result["log"].append(f"{weapon.name} (strength {weapon.strength})"
                         f" against {defender.name} (toughness {defender.toughness})"
                         f" requires {success_threshold}+ to wound.")

    wounds = roll_dice(len(hits), success_threshold=success_threshold)
    result["log"].append(f"{wounds} => {len(wounds)} attacks were wounding.")

    if not wounds:
        return result

    save_threshold = min(parse_stat(defender.save) - weapon.armour_penetration, 6)
    result["log"].append(f"{defender.name} (save value {defender.save})"
                         f" is modified by {weapon.name} (armour penetration {weapon.armour_penetration})"
                         f" and therefore requires {save_threshold}+ to save (max 6).")
    saved_wounds = roll_dice(len(wounds), success_threshold=save_threshold)
    result["log"].append(f"{saved_wounds} => {len(saved_wounds)} / {len(wounds)} wounds were saved.")

    unsaved_wounds = len(wounds) - len(saved_wounds)
    if unsaved_wounds:
        damage = unsaved_wounds * weapon.damage
        result["log"].append(f"{len(wounds) - len(saved_wounds)} wounds * {weapon.damage} weapon damage => {damage} damage inflicted.")
        result["damage"] = damage

    return result
