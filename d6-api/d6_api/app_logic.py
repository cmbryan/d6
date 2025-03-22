from pathlib import Path
import re

from .models import Unit, Weapon
from .util import parse_stat, roll_dice, to_int

current_module_dir = Path(__file__).resolve().parent


def simulate_attack(attacker_name, attack_unit_size, defender_name, weapon_name):
    """
    Simulates an attack. Currently hard-coded to use the 40k, 10th edition ruleset.

    Args:
        attacker_name (str): The name of the attacking unit.
        attack_unit_size (int): The number of models in the attacking unit.
        defender_name (str): The name of the defending unit.
        weapon_name (str): The name of the weapon used by the attacker.

    Returns:
        dict: A dictionary containing the result of the attack simulation, including the total damage inflicted and a log of actions.
    """

    result = {"log": [], "damage": 0}
    
    attacker = Unit.query.where(Unit.name == attacker_name).first()
    defender = Unit.query.where(Unit.name == defender_name).first()
    weapon = Weapon.query.where(Weapon.name == weapon_name).first()

    assert attacker, f"Attacker '{attacker_name}' not found."
    assert defender, f"Defender '{defender_name}' not found."
    assert weapon in attacker.weapons, f"{attacker_name} does not have a {weapon_name}."

    random_attacks = re.match(r"(?P<num_dice>\d+)?D6(\+(?P<modifier>\d+))?", str(weapon.attacks))
    if random_attacks:
        num_dice = (to_int(random_attacks.group("num_dice")) or 1) * attack_unit_size
        modifier = to_int(random_attacks.group("modifier"))
        roll = sum(roll_dice(num_dice))
        attacks = roll + num_dice * modifier
        result["log"].append(f"{attacker_name} x{attack_unit_size} rolled for random attacks ({weapon.attacks}) => {attacks}.")
    else:
        # Normal attacks
        attacks = weapon.attacks * attack_unit_size
    result["log"].append(f"{attacker_name} x{attack_unit_size} attacks {attacks} times.")

    result["log"].append(f"{weapon_name} requires {parse_stat(weapon.weapon_skill)}+ to hit.")
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
    result["log"].append(f"{weapon_name} (strength {weapon.strength})"
                         f" against {defender_name} (toughness {defender.toughness}"
                         f" requires {success_threshold}+ to wound.")

    wounds = roll_dice(len(hits), success_threshold=success_threshold)
    result["log"].append(f"{wounds} => {len(wounds)} attacks were wounding.")

    if not wounds:
        return result

    save_threshold = min(parse_stat(defender.save) - weapon.armour_penetration, 6)
    result["log"].append(f"{defender_name} (save value {defender.save})"
                         f" is modified by {weapon_name} (armour penetration {weapon.armour_penetration}"
                         f" and therefore requires {save_threshold}+ to save (max 6).")
    saved_wounds = roll_dice(len(wounds), success_threshold=save_threshold)
    result["log"].append(f"{saved_wounds} => {len(saved_wounds)} / {len(wounds)} wounds were saved.")

    unsaved_wounds = len(wounds) - len(saved_wounds)
    if unsaved_wounds:
        damage = unsaved_wounds * weapon.damage
        result["log"].append(f"{len(wounds) - len(saved_wounds)} wounds * {weapon.damage} weapon damage => {damage} damage inflicted.")
        result["damage"] = damage

    return result
