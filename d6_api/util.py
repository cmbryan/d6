import json
from pathlib import Path
import random
from dotdict import dotdict
from flask import Flask

import d6_api
from .models import db, association_tables

_FACES = ["\u2680", "\u2681", "\u2682", "\u2683", "\u2684", "\u2685"]


def roll_dice(num_dice: int, sides=6, success_threshold=0):
    """Simulate a dice roll.

    Args:
        num_dice (int): number of dice
        sides (int, optional): Number of sides on each die. Defaults to 6.
        success_threshold (int, optional): The minimum required to be successful. Defaults to 0.

    Returns:
        tuple(int, list(int)): num_success, dice_result
    """

    roll = [random.randint(1, sides) for _ in range(num_dice)]
    success = [d for d in roll if d>=success_threshold]
    return (len(success), roll)


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


__data_filepath = Path(d6_api.__file__).resolve().parent / "data" / "data.json"

def dump_db(app: Flask):
    """
    Dumps the database to a dictionary for version control.
    """
    with open(__data_filepath, "w") as fh:
        with app.app_context():
            table_data = {
                "objects": {
                    **{
                        t.__tablename__: [row.to_table_dict() for row in t.query.all()]
                        for t in db.Model.__subclasses__()
                        if hasattr(t, "__tablename__")
                    }
                },
                "associations": {
                    **{
                        t.name: [dict(row._mapping) for row in db.session.query(t).all()]
                        for t in association_tables
                    }
                },
            }
            json.dump(table_data, fh)

def create_db(app: Flask):
    """
    Creates a database from the serialized data.
    """
    with open(__data_filepath, "r") as fh:
        data = json.load(fh)

    with app.app_context():
        db.drop_all()
        db.create_all()

        model_dict = {
            model.__name__.lower(): model for model in db.Model.__subclasses__()
        }
        association_dict = {
            t.name: t for t in association_tables
        }

        # Insert model data
        for table_name, rows in data["objects"].items():
            table = model_dict.get(table_name)
            if table is not None:
                print(f"Loading {len(rows)} rows into {table_name}...")
                for row_data in rows:
                    row = table(**row_data)
                    db.session.add(row)
            else:
                raise ValueError(f"Table '{table_name}' not found.")

        # Insert association data
        for table_name, rows in data["associations"].items():
            table = association_dict.get(table_name)
            if table is not None:
                print(f"Loading {len(rows)} rows into {table_name}...")
                for row_data in rows:
                    db.session.execute(table.insert().values(row_data))
            else:
                raise ValueError(f"Table '{table_name}' not found.")

        db.session.commit()
