from pathlib import Path
import re
import tomllib as tl

from .util import convert_to_dot_dict, parse_stat, roll_dice, to_int

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


def simulate_attack(attacker_name, defender_name, weapon_name):
    attacker = datasheets[attacker_name]
    defender = datasheets[defender_name]
    weapon = attacker.Weapons[weapon_name]

    attacks = weapon.attacks
    random_attacks = re.match(r"(?P<num_dice>)?D6(\+(?P<modifier>\d))", str(weapon.attacks))
    if random_attacks:
        num_dice = to_int(random_attacks.group("num_dice")) or 1
        modifier = to_int(random_attacks.group("modifier"))
        roll = sum(roll_dice(num_dice))
        attacks = roll + num_dice * modifier

    hits = roll_dice(attacks, success_threshold=parse_stat(weapon.weapon_skill))

    if not hits:
        return {"message": "No hits! Attack sequence ends."}

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
    else:
        return {"message": "Error: Could not determine to wound roll"}

    wounds = roll_dice(len(hits), success_threshold=success_threshold)

    if not wounds:
        return {"message": "No wounds! Attack sequence ends."}

    save_threshold = min(parse_stat(defender.save) - weapon.armour_penetration, 6)
    saved_wounds = len(roll_dice(len(wounds), success_threshold=save_threshold))

    total_damage = (len(wounds) - saved_wounds) * weapon.damage

    return {
        "damage_inflicted": total_damage,
        "message": f"{defender.name} takes {total_damage} damage."
    }