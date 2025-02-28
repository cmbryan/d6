import random
import json

# Load datasheet data from a JSON file
try:
    with open("warhammer_datasheets_10e.json", "r") as f:
        datasheets = json.load(f)
except FileNotFoundError:
    print("Error: Datasheet file 'warhammer_datasheets_10e.json' not found.")
    exit()
except json.JSONDecodeError:
    print("Error: Invalid JSON format in 'warhammer_datasheets_10e.json'.")
    exit()

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

# Example Datasheet (replace with your full dataset)
example_datasheets = {
    "Space Marine Intercessor": {
        "name": "Space Marine Intercessor",
        "toughness": 4,
        "save": 3,
        "weapon": {
            "name": "Bolt Rifle",
            "attacks": 3,
            "strength": 4,
            "armor_penetration": 0,
            "damage": 1,
            "to_hit": 3,
        },
        "to_wound": 4, #simplified to_wound
    },
    "Ork Boy": {
        "name": "Ork Boy",
        "toughness": 5,
        "save": 6,
        "weapon": {
            "name": "Slugga",
            "attacks": 2,
            "strength": 4,
            "armor_penetration": 0,
            "damage": 1,
            "to_hit": 4,
        },
        "to_wound": 4, #simplified to_wound
    },
    "Terminator":{
        "name": "Terminator",
        "toughness": 5,
        "save": 2,
        "invulnerable_save": 4,
        "weapon":{
            "name": "Power Fist",
            "attacks": 3,
            "strength": 9,
            "armor_penetration": 2,
            "damage": 2,
            "to_hit": 3,
        },
        "to_wound": 4, #simplified to_wound
    }

}

# Save Example datasheets to Json.
with open("warhammer_datasheets_10e.json", "w") as outfile:
    json.dump(example_datasheets, outfile, indent=4)

# User Input
attacker_name = input("Enter attacker unit name: ")
defender_name = input("Enter defender unit name: ")

attacker_unit = get_unit(attacker_name)
defender_unit = get_unit(defender_name)

if attacker_unit and defender_unit:
    simulate_attack(attacker_unit, defender_unit)