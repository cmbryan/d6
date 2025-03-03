from ..app_logic import simulate_attack

def test_simulate_attack(mocker):

    # No hits
    with mocker.patch('d6_api.app_logic.roll_dice', return_value=[]):
        result = simulate_attack(
            "Captain in Terminator Armour",
            "Psychophage",
            "Relic weapon"
        )
        assert result == {"message": "No hits! Attack sequence ends."}

    # Hits, but no wounds
    with mocker.patch('d6_api.app_logic.roll_dice', side_effect=[[1], []]):
        result = simulate_attack(
            "Captain in Terminator Armour",
            "Psychophage",
            "Relic weapon"
        )
        assert result == {"message": "No wounds! Attack sequence ends."}

    # Hit and wound, but save
    with mocker.patch('d6_api.app_logic.roll_dice', side_effect=[[1], [1], [1]]):
        result = simulate_attack(
            "Captain in Terminator Armour",
            "Psychophage",
            "Relic weapon"
        )
        assert result == {
            "damage_inflicted": 0,
            "message": "Psychophage takes 0 damage."
        }

    # Hit and wound, no save
    with mocker.patch('d6_api.app_logic.roll_dice', side_effect=[[1], [1], []]):
        result = simulate_attack(
            "Captain in Terminator Armour",
            "Psychophage",
            "Relic weapon"
        )
        assert result == {
            "damage_inflicted": 2,
            "message": "Psychophage takes 2 damage."
        }
