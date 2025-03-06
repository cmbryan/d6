from pathlib import Path
import re
import tomllib as tl

from util import convert_to_dot_dict, parse_stat, roll_dice, to_int

current_module_dir = Path(__file__).resolve().parent

# Load datasheet data from a TOML file
datasheets_path = current_module_dir / "data" / "warhammer_datasheets_10e.toml"

try:
    with open(datasheets_path, "rb") as f:
        datasheets = convert_to_dot_dict(tl.load(f))
except FileNotFoundError:
    raise RuntimeError(f"Error: Datasheet file '{datasheets_path}' not found.")
except tl.TOMLDecodeError:
    raise RuntimeError(f"Error: Invalid format in '{datasheets_path}'.")
units = list(datasheets.keys())
weapons = sum([list(datasheets[unit].Weapons.keys()) for unit in datasheets], [])


def simulate_attack(attacker_name, defender_name, weapon_name):
    """
    Simulates an attack. Currently hard-coded to use the 40k, 10th edition ruleset.

    Args:
        attacker_name (str): The name of the attacking unit.
        defender_name (str): The name of the defending unit.
        weapon_name (str): The name of the weapon used by the attacker.

    Returns:
        dict: A dictionary containing the result of the attack simulation, including the total damage inflicted and a log of actions.
    """

    result = {"log": [], "damage": 0}
    
    attacker = datasheets[attacker_name]
    defender = datasheets[defender_name]
    weapon = attacker.Weapons[weapon_name]

    attacks = weapon.attacks
    random_attacks = re.match(r"(?P<num_dice>)?D6(\+(?P<modifier>\d))", str(weapon.attacks))
    if random_attacks:
        num_dice = to_int(random_attacks.group("num_dice")) or 1
        modifier = to_int(random_attacks.group("modifier"))
        roll = sum(roll_dice(num_dice))
        result["log"].append(f"{attacker_name} rolled for random attacks ({random_attacks}) => {len(attacks)}.")
        attacks = roll + num_dice * modifier
    result["log"].append(f"{attacker_name} attacks {attacks} times.")

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
