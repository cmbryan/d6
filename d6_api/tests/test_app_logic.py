import pytest

from d6_api.app_logic import roll_to_hit, roll_to_wound


@pytest.mark.usefixtures("client")
def test_roll_to_hit(client, mocker):
    with client.application.app_context():
        # No hits
        mocker.patch("d6_api.app_logic.roll_dice", return_value=[0, [1, 1, 1, 1]])
        num_hits, roll, log = roll_to_hit(
            attacker_id=1,
            unit_size=2,
            defender_id=1,
            weapon_id=1,
        )
        assert num_hits == 0
        assert roll == [1, 1, 1, 1]
        assert log == [
            "Captain in Terminator Armour x2 with Storm bolter (2 attacks) for a total of 4 attacks.",
            "Storm bolter requires 3+ to hit.",
            "[1, 1, 1, 1] => 0 attacks were successful.",
        ]

        # Hits
        mocker.patch("d6_api.app_logic.roll_dice", return_value=[2, [3, 3, 1, 1]])
        num_hits, roll, log = roll_to_hit(
            attacker_id=1,
            unit_size=2,
            defender_id=1,
            weapon_id=1,
        )
        assert num_hits == 2
        assert roll == [3, 3, 1, 1]
        assert log == [
            "Captain in Terminator Armour x2 with Storm bolter (2 attacks) for a total of 4 attacks.",
            "Storm bolter requires 3+ to hit.",
            "[3, 3, 1, 1] => 2 attacks were successful.",
        ]

@pytest.mark.usefixtures("client")
def test_roll_to_wound(client, mocker):
    with client.application.app_context():
        # Hit and wound, but save
        mocker.patch("d6_api.app_logic.roll_dice", return_value=[0, [4, 4, 4, 4]])
        num_wounds, roll, log = roll_to_wound(
             attacker_id=1,
             num_attacks=2,
             defender_id=1,
             weapon_id=1,
        )
        assert num_wounds == 0
        assert roll == [4, 4, 4, 4]
        assert log == [
            "Storm bolter (strength 4) against Captain in Terminator Armour (toughness 5) requires 5+ to wound.",
            "[4, 4, 4, 4] => 0 attacks were wounding.",
        ]

        # Hit and wound, not saved
        mocker.patch("d6_api.app_logic.roll_dice", return_value=[2, [4, 5, 6, 4]])
        num_wounds, roll, log = roll_to_wound(
             attacker_id=1,
             num_attacks=2,
             defender_id=1,
             weapon_id=1,
        )
        assert num_wounds == 2
        assert roll == [4, 5, 6, 4]
        assert log == [
            "Storm bolter (strength 4) against Captain in Terminator Armour (toughness 5) requires 5+ to wound.",
            "[4, 5, 6, 4] => 2 attacks were wounding.",
        ]
