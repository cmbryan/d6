from pathlib import Path
import random
import tomllib as tl

current_module_dir = Path(__file__).resolve().parent

# Load datasheet data from a TOML file
datasheet = current_module_dir / "data" / "warhammer_datasheets_10e.toml"

try:
    print(datasheet.absolute())
    with open(datasheet, "rb") as f:
        datasheets = tl.load(f)
except FileNotFoundError:
    print(f"Error: Datasheet file '{datasheet}' not found.")
    exit(1)
except tl.TOMLDecodeError:
    print(f"Error: Invalid format in '{datasheet}'.")
    exit(1)

def roll_dice(num_dice, sides=6):
    """Simulates rolling multiple dice."""

    return [random.randint(1, sides) for _ in range(num_dice)]

def get_unit(unit_name):
    """Retrieves a unit's datasheet."""

    if unit_name in datasheets:
        return datasheets[unit_name]
    else:
        print(f"Unit '{unit_name}' not found.")
        return None

def simulate_attack(attacker, defender):
    """Simulates an attack sequence."""

    weapon = attacker["weapon"]  # Assuming one weapon for simplicity.
    attacks = weapon["attacks"]
    strength = weapon["strength"]
    armor_penetration = weapon["armor_penetration"]
    damage = weapon["damage"]
    to_hit = weapon["to_hit"]
    to_wound = attacker["to_wound"] #simplified for this example, in reality, it would be based on the defender's toughness.

    toughness = defender["toughness"]
    save = defender["save"]
    invulnerable_save = defender.get("invulnerable_save", 99) # 99 means no invuln save.

    print(f"\n--- {attacker['name']} attacks {defender['name']} ---")
    print(f"{attacker['name']} attacks with {weapon['name']} ({attacks} attacks).")

    # To Hit Rolls
    hit_rolls = roll_dice(attacks)
    hits = [roll for roll in hit_rolls if roll >= to_hit]
    num_hits = len(hits)
    print(f"To Hit: {hit_rolls} ({num_hits} hits)")

    if num_hits == 0:
        print("No hits! Attack sequence ends.")
        return

    # To Wound Rolls
    wound_rolls = roll_dice(num_hits)
    wounds = []
    for roll in wound_rolls:
        if strength >= (toughness * 2):
            if roll >= 2:
                wounds.append(roll)
        elif strength > toughness:
            if roll >= 3:
                wounds.append(roll)
        elif strength == toughness:
            if roll >= 4:
                wounds.append(roll)
        elif strength < toughness:
            if roll >= 5:
                wounds.append(roll)
        elif strength <= (toughness / 2):
            if roll >= 6:
                wounds.append(roll)
        else:
            print("Error: Could not determine to wound roll")
    num_wounds = len(wounds)

    print(f"To Wound: {wound_rolls} ({num_wounds} wounds)")

    if num_wounds == 0:
        print("No wounds! Attack sequence ends.")
        return

    # Saving Throws
    saved_wounds = 0
    failed_saves = 0
    for _ in range(num_wounds):
        save_roll = random.randint(1, 6)
        modified_save = save + armor_penetration
        if modified_save > 6:
            modified_save = 6
        if save_roll >= min(modified_save, invulnerable_save):
            saved_wounds += 1
        else:
            failed_saves +=1
    print(f"Saving Throws: {num_wounds} wounds, {saved_wounds} saved, {failed_saves} failed.")

    # Damage Application
    total_damage = failed_saves * damage
    print(f"Damage inflicted: {total_damage}")

    # Simplified damage application. In a real game, you'd track unit health.
    print(f"{defender['name']} takes {total_damage} damage.")

# User Input
attacker_name = input("Enter attacker unit name: ")
defender_name = input("Enter defender unit name: ")

attacker_unit = get_unit(attacker_name)
defender_unit = get_unit(defender_name)

if attacker_unit and defender_unit:
    simulate_attack(attacker_unit, defender_unit)