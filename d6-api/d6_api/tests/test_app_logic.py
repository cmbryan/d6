import pytest
from d6_api.app_logic import simulate_attack


@pytest.mark.usefixtures("client")
def test_simulate_attack(client, mocker):
    with client.application.app_context():
        # No hits
        mocker.patch("d6_api.app_logic.roll_dice", return_value=[])
        result = simulate_attack(
            1, 2, 1, 1
        )
        assert result == {
            "log": [
                "Captain in Terminator Armour x2 with Storm bolter (2 attacks) for a total of 4 attacks.",
                "Storm bolter requires 3+ to hit.",
                "[] => 0 attacks were successful.",
            ],
            "damage": 0,
        }

        # Hits, but no wounds
        mocker.patch("d6_api.app_logic.roll_dice", side_effect=[[1], []])
        result = simulate_attack(
            1, 2, 1, 1
        )
        assert result == {
            "log": [
                "Captain in Terminator Armour x2 with Storm bolter (2 attacks) for a total of 4 attacks.",
                "Storm bolter requires 3+ to hit.",
                "[1] => 1 attacks were successful.",
                "Storm bolter (strength 4) against Captain in Terminator Armour (toughness 5) requires 5+ to wound.",
                "[] => 0 attacks were wounding.",
            ],
            "damage": 0,
        }

        # Hit and wound, but save
        mocker.patch("d6_api.app_logic.roll_dice", side_effect=[[1], [1], [1]])
        result = simulate_attack(
            1, 2, 1, 1
        )
        assert result == {
            "log": [
                "Captain in Terminator Armour x2 with Storm bolter (2 attacks) for a total of 4 attacks.",
                "Storm bolter requires 3+ to hit.",
                "[1] => 1 attacks were successful.",
                "Storm bolter (strength 4) against Captain in Terminator Armour (toughness 5) requires 5+ to wound.",
                "[1] => 1 attacks were wounding.",
                "Captain in Terminator Armour (save value 2+) is modified by Storm bolter (armour penetration 0) and therefore requires 2+ to save (max 6).",
                "[1] => 1 / 1 wounds were saved.",
            ],
            "damage": 0,
        }

        # Hit and wound, no save
        mocker.patch("d6_api.app_logic.roll_dice", side_effect=[[1], [1], []])
        result = simulate_attack(
            "1", 2, 1, 1
        )
        assert result == {
            "log": [
                "Captain in Terminator Armour x2 with Storm bolter (2 attacks) for a total of 4 attacks.",
                "Storm bolter requires 3+ to hit.",
                "[1] => 1 attacks were successful.",
                "Storm bolter (strength 4) against Captain in Terminator Armour (toughness 5) requires 5+ to wound.",
                "[1] => 1 attacks were wounding.",
                "Captain in Terminator Armour (save value 2+) is modified by Storm bolter (armour penetration 0) and therefore requires 2+ to save (max 6).",
                "[] => 0 / 1 wounds were saved.",
                "1 wounds * 1 weapon damage => 1 damage inflicted.",
            ],
            "damage": 1,
        }
