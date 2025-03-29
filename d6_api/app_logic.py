from pathlib import Path
import re

from .models import Unit, Weapon, db
from .util import parse_stat, roll_dice, to_int

current_module_dir = Path(__file__).resolve().parent


def roll_to_hit(attacker_id: int, unit_size: int, defender_id: int, weapon_id: int):
    """
    Roll-to-hit, the first step of a 40k, 10th edition attack sequence.

    Args:
        attacker_id (int): The id of the attacking unit.
        attack_unit_size (int): The number of models in the attacking unit.
        defender_id (int): The id of the defending unit.
        weapon_id (int): The id of the weapon used by the attacker.

    Returns:
        tuple(int, list(int), list(str)): Number of hits, a list of the dice numbers, and a log of actions.
    """

    attacker = db.session.get(Unit, attacker_id)
    defender = db.session.get(Unit, defender_id)
    weapon = db.session.get(Weapon, weapon_id)
    log = []

    assert attacker, f"Attacker id:{attacker_id} not found."
    assert defender, f"Defender id:{defender_id} not found."
    assert weapon in attacker.weapons, f"{attacker.name} does not have a weapon id:{weapon_id}."

    # Number of attacks
    random_attacks = re.match(r"(?P<num_dice>\d+)?D6(\+(?P<modifier>\d+))?", str(weapon.attacks))
    if random_attacks:
        num_dice = (to_int(random_attacks.group("num_dice")) or 1) * unit_size
        modifier = to_int(random_attacks.group("modifier"))
        roll = sum(roll_dice(num_dice))
        num_attacks = roll + num_dice * modifier
        log.append(f"{attacker.name} x{unit_size} rolled for random attacks ({weapon.attacks}) => {num_attacks}.")
    else:
        # Normal attacks
        num_attacks = weapon.attacks * unit_size
    log.append(f"{attacker.name} x{unit_size} with {weapon.name} ({weapon.attacks} attacks) for a total of {num_attacks} attacks.")

    # Number of hits
    num_hits, roll = roll_dice(num_attacks, success_threshold=parse_stat(weapon.weapon_skill))
    log.append(f"{weapon.name} requires {parse_stat(weapon.weapon_skill)}+ to hit.")
    log.append(f"{roll} => {num_hits} attacks were successful.")

    return num_hits, roll, log


def roll_to_wound(attacker_id: int, num_attacks: int, defender_id: int, weapon_id: int):
    """
    Roll-to-wound, the second step of a 40k, 10th edition attack sequence.

    Args:
        attacker_id (int): The id of the attacking unit.
        num_attacks (int): The number of attacks being performed.
        defender_id (int): The id of the defending unit.
        weapon_id (int): The id of the weapon used by the attacker.

    Returns:
        tuple(int, list(int), list(str)): Number of wounds, a list of the dice numbers, and a log of actions.
    """

    attacker = db.session.get(Unit, attacker_id)
    defender = db.session.get(Unit, defender_id)
    weapon = db.session.get(Weapon, weapon_id)
    log = []

    assert attacker, f"Attacker id:{attacker_id} not found."
    assert defender, f"Defender id:{defender_id} not found."
    assert weapon in attacker.weapons, f"{attacker.name} does not have a weapon id:{weapon_id}."

    if weapon.strength >= (defender.toughness * 2):
        success_threshold = 2
    elif weapon.strength > defender.toughness:
        success_threshold = 3
    elif weapon.strength == defender.toughness:
        success_threshold = 4
    elif weapon.strength < defender.toughness:
        success_threshold = 5
    else:  # weapon.strength * 2 <= defendender.toughness
        success_threshold = 6
    log.append(f"{weapon.name} (strength {weapon.strength}) against {defender.name} (toughness {defender.toughness}) requires {success_threshold}+ to wound.")

    # Number of wounds
    num_wounds, roll = roll_dice(num_attacks, success_threshold=success_threshold)
    log.append(f"{roll} => {num_wounds} attacks were wounding.")

    return num_wounds, roll, log


def roll_to_save(num_wounds: int, defender_id: int, weapon_id: int):
    """
    Roll-to-save, the third step of a 40k, 10th edition attack sequence.

    Args:
        attacker_id (int): The id of the attacking unit.
        num_wounds (int): The number of wounds being inflicted.
        defender_id (int): The id of the defending unit.
        weapon_id (int): The id of the weapon used by the attacker.

    Returns:
        tuple(int, list(int), list(str)): Number of wounds NOT saved, a list of the dice numbers, and a log of actions.
    """

    defender = db.session.get(Unit, defender_id)
    weapon = db.session.get(Weapon, weapon_id)
    log = []

    success_threshold = defender.save - weapon.armour_penetration
    log.append(f"{defender.name} (save value {defender.save})"
               f" is modified by {weapon.name} (armour penetration {weapon.armour_penetration})"
               f" and therefore requires {success_threshold}+ to save (max 6).")

    # Number of wounds saved
    num_saved_wounds, roll = roll_dice(num_wounds, success_threshold=success_threshold)
    log.append(f"{roll} => {num_saved_wounds} / {num_wounds} wounds were saved.")

    return num_wounds - num_saved_wounds, roll, log


def inflict_damage(num_unsaved_wounds: int, weapon_id: int):
    """
    Inflict damage, the final step of a 40k, 10th edition attack sequence.

    Args:
        num_unsaved_wounds (int): The number of wounds NOT saved.
        weapon_id (int): The id of the weapon used by the attacker.

    Returns:
        tuple(int, list(str)): The total damage inflicted, and a log of actions.
    """

    weapon = db.session.get(Weapon, weapon_id)
    damage = num_unsaved_wounds * weapon.damage
    log = [f"{num_unsaved_wounds} * {weapon.damage} weapon damage => {damage} damage inflicted."]
    return damage, log
