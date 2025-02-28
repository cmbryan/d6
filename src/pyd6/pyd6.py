from pathlib import Path
import re
import tomllib as tl

from util import convert_to_dot_dict, parse_stat, roll_dice, to_int

current_module_dir = Path(__file__).resolve().parent

# Load datasheet data from a TOML file
datasheets_path = current_module_dir / "data" / "warhammer_datasheets_10e.toml"

try:
    print(datasheets_path.absolute())
    with open(datasheets_path, "rb") as f:
        datasheets = convert_to_dot_dict(tl.load(f))
except FileNotFoundError:
    print(f"Error: Datasheet file '{datasheets_path}' not found.")
    exit(1)
except tl.TOMLDecodeError:
    print(f"Error: Invalid format in '{datasheets_path}'.")
    exit(1)

def simulate_attack(attacker, defender):
    """Simulates an attack sequence."""

    # Choose a weapon
    weapon_name_list = list(attacker.Weapons.keys())
    for idx, weapon_name in enumerate(weapon_name_list):
        print(f"{idx} - {weapon_name}")
    weapon_name = weapon_name_list[int(input("Enter index of chosen weapon: "))]
    weapon = attacker.Weapons[weapon_name]

    # Work out number of attacks
    # This is either a plain number of dice, or a roll to detirmine the number of dynamic attacks
    attacks = weapon.attacks
    dynamic_attacks = re.match(r"(?P<num_dice>)?D6(\+(?P<modifier>\d))", str(weapon.attacks))
    if dynamic_attacks:
        num_dice = to_int(dynamic_attacks.group("num_dice")) or 1
        modifier = to_int(dynamic_attacks.group("modifier"))
        roll = sum(roll_dice(num_dice))
        attacks = roll + num_dice*modifier  # Check this modifier logic. Does it even happen?
        print(f"  Number of attacks is {roll} + {num_dice}*{modifier} => {attacks}")

    # invulnerable_save = defender.get("invulnerable_save", 99) # 99 means no invuln save.

    print(f"\n\U0001F5E1 \U0001F5E1 \U0001F5E1  \033[31m{attacker.name}\033[0m"
          " attacks"
          f" \033[34m{defender.name}\033[0m \U0001F6E1\uFE0F \U0001F6E1\uFE0F \U0001F6E1\uFE0F")

    print(f"  Attacking with {weapon.name} ({attacks} attacks)...")

    # To Hit Rolls
    hits = roll_dice(attacks, success_threshold=parse_stat(weapon.weapon_skill))
    print(f"  Hits: {hits} ({len(hits)})")

    if not hits:
        print("  No hits! Attack sequence ends.")
        return

    # Wound Rolls
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
        print("  Error: Could not determine to wound roll")
        return

    print(f"  {weapon.name}'s strength is {weapon.strength}, {defender.name}'s toughness is {defender.toughness},"
          f" therefore a {success_threshold}+ is required to inflict damage")

    wounds = roll_dice(len(hits), success_threshold=success_threshold)
    print(f"  Wounds: {wounds} ({len(wounds)})")

    if not wounds:
        print("  No wounds! Attack sequence ends.")
        return

    # Saving Throws
    save_threshold = min(parse_stat(defender.save) - weapon.armour_penetration, 6)  # AP is negative
    print(f"Save threshold is {parse_stat(defender.save)} - {weapon.armour_penetration} => {save_threshold}")
    saved_wounds = len(roll_dice(len(wounds), success_threshold=save_threshold))
    print(f"  Wounds saved: {saved_wounds} saved.")

    # Damage Application
    total_damage = (len(wounds) - saved_wounds) * weapon.damage
    print(f"  Damage inflicted: {len(wounds) - saved_wounds} * {weapon.damage} => {total_damage}")

    # Simplified damage application. In a real game, you'd track unit health.
    print(f"\n  \033[34m{defender.name}\033[0m takes {total_damage} damage.")

# Choose attacker and defender
unit_name_list = list(datasheets.keys())
for idx, unit_name in enumerate(unit_name_list):
    print(f"{idx} - {unit_name}")
attacker_name = unit_name_list[int(input("Enter index of attacking unit: "))]
attacker_unit = datasheets[attacker_name]
defender_name = unit_name_list[int(input("Enter index of defending unit: "))]
defender_unit = datasheets[defender_name]

simulate_attack(attacker_unit, defender_unit)