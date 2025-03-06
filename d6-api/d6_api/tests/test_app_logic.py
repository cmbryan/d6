from app_logic import simulate_attack


def test_simulate_attack(mocker):
    # No hits
    mocker.patch("app_logic.roll_dice", return_value=[])
    result = simulate_attack(
        "Captain in Terminator Armour", 2, "Psychophage", "Relic weapon"
    )
    assert result == {
        "log": [
            "Captain in Terminator Armour x2 attacks 10 times.",
            "[] => 0 attacks were successful.",
        ],
        "damage": 0,
    }

    # Hits, but no wounds
    mocker.patch("app_logic.roll_dice", side_effect=[[1], []])
    result = simulate_attack(
        "Captain in Terminator Armour", 2, "Psychophage", "Relic weapon"
    )
    assert result == {
        "log": [
            "Captain in Terminator Armour x2 attacks 10 times.",
            "[1] => 1 attacks were successful.",
            "Relic weapon (strength 5) against Psychophage (toughness 9 requires 5+ to wound.",
            "[] => 0 attacks were wounding.",
        ],
        "damage": 0,
    }

    # Hit and wound, but save
    mocker.patch("app_logic.roll_dice", side_effect=[[1], [1], [1]])
    result = simulate_attack(
        "Captain in Terminator Armour", 2, "Psychophage", "Relic weapon"
    )
    assert result == {
        "log": [
            "Captain in Terminator Armour x2 attacks 10 times.",
            "[1] => 1 attacks were successful.",
            "Relic weapon (strength 5) against Psychophage (toughness 9 requires 5+ to wound.",
            "[1] => 1 attacks were wounding.",
            "Psychophage (save value 3+) is modified by Relic weapon (armour penetration -2 and therefore requires 5+ to save (max 6).",
            "[1] => 1 / 1 wounds were saved.",
        ],
        "damage": 0,
    }

    # Hit and wound, no save
    mocker.patch("app_logic.roll_dice", side_effect=[[1], [1], []])
    result = simulate_attack(
        "Captain in Terminator Armour", 2, "Psychophage", "Relic weapon"
    )
    assert result == {
        "log": [
            "Captain in Terminator Armour x2 attacks 10 times.",
            "[1] => 1 attacks were successful.",
            "Relic weapon (strength 5) against Psychophage (toughness 9 requires 5+ to wound.",
            "[1] => 1 attacks were wounding.",
            "Psychophage (save value 3+) is modified by Relic weapon (armour penetration -2 and therefore requires 5+ to save (max 6).",
            "[] => 0 / 1 wounds were saved.",
            "1 wounds * 2 weapon damage => 2 damage inflicted.",
        ],
        "damage": 2,
    }
