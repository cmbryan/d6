from dataclasses import asdict
import json
from pathlib import Path
import random
from dotdict import dotdict
from flask import Flask

import d6_api
from .models import db

_FACES = ["\u2680", "\u2681", "\u2682", "\u2683", "\u2684", "\u2685"]


def roll_dice(num_dice, sides=6, success_threshold=0):
    """Simulates rolling multiple dice."""

    roll = [random.randint(1, sides) for _ in range(num_dice)]
    success = [d for d in roll if d>=success_threshold]
    fail = [d for d in roll if d<success_threshold]

    # Display
    if success_threshold > 0:
        print("  => " + " ".join(_FACES[d - 1] for d in success))
        print("  => " + " ".join(_FACES[d - 1] for d in fail))
    else:
        print(" ".join(_FACES[d - 1] for d in roll))

    return success if success_threshold else roll


def convert_to_dot_dict(data):
    """
    Converts a nested dictionary to a DotDict.
    """
    if isinstance(data, dict):
        return dotdict({k: convert_to_dot_dict(v) for k, v in data.items()})
    elif isinstance(data, list):
        return [convert_to_dot_dict(item) for item in data] # recursive conversion of list items.
    else:
        return data


def parse_stat(stat: str):
    """
    Removes the + modifier and converts to an int
    """

    return int(stat.replace("+", ""))


def to_int(input: str) -> int:
    """
    Returns int(input) or 0
    """
    return int(input) if input else 0


def dump_db(app: Flask):
    """
    Dumps the database to a dictionary for version control.
    """

    filepath = Path(d6_api.__file__).resolve().parent / "data" / "data.json"
    with open(filepath, "w") as fh:
        with app.app_context():
            json.dump(
                {
                    t.__tablename__: [row.to_dict() for row in t.query.all()]
                    for t in db.Model.__subclasses__()
                    if hasattr(t, "__tablename__")
                },
                fh,
            )
