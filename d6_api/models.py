from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy import Column, ForeignKey, Integer, MetaData, Table

class Model(DeclarativeBase, MappedAsDataclass):
    """
    Base class for SQLAlchemy models with a custom naming convention for constraints.
    """
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',  # index
        "uq": "uq_%(table_name)s_%(column_0_name)s",  # unique constraint
        "ck": "ck_%(table_name)s_%(constraint_name)s",  # check constraint
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",  # foreign key
        "pk": "pk_%(table_name)s",  # primary key
    })


    def serialize(self):
        """
        Serializes a SQLAlchemy model instance into a dictionary.
        Handles both attributes and relationships.

        Args:
            self: The SQLAlchemy model instance to serialize.

        Returns:
            dict: A dictionary representation of the model instance.
        """
        if self is None:
            return None

        # Get the model's attributes
        data = {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}

        # Get the model's relationships
        for rel in inspect(self).mapper.relationships:
            rel_val = getattr(self, rel.key)
            if rel.uselist:
                data[rel.key] = [child.id for child in rel_val]
            else:
                data[rel.key] = rel_val.id

        return data



class AssociationTable(Table):
    def to_table_dict(self):
        return {column.name: getattr(self, column.name) for column in self.columns}


db = SQLAlchemy(model_class=Model)
al = Alembic(metadatas=Model.metadata)

unit_weapon_association = AssociationTable(
    'unit_weapon_association',
    Model.metadata,
    Column('unit_id', Integer, ForeignKey('unit.id'), primary_key=True),
    Column('weapon_id', Integer, ForeignKey('weapon.id'), primary_key=True)
)

association_tables = [unit_weapon_association]


class Category(db.Model):
    name: Mapped[str] = mapped_column(primary_key=True)
    customizable: Mapped[bool] = mapped_column(default=False)


class Unit(db.Model):
    name: Mapped[str] = mapped_column(unique=True)
    category: Mapped[Category] = mapped_column(ForeignKey("category.name"))
    toughness: Mapped[int] = mapped_column(default=1)
    save: Mapped[str] = mapped_column(default="1+")
    invulnerable_save: Mapped[str] = mapped_column(default="")

    weapons: Mapped[list["Weapon"]] = relationship("Weapon", secondary=unit_weapon_association, back_populates="units", default_factory=list)
    id: Mapped[int|None] = mapped_column(primary_key=True, autoincrement=True, default=None, nullable=False)

    def __init__(self, *args, **kwargs):
        """ Override to handle weapon_ids parameter """
        weapons = [db.session.get(Weapon, w_id) for w_id in kwargs.pop("weapon_ids", [])]
        return super().__init__(*args, weapons=weapons, **kwargs)


class Weapon(db.Model):
    name: Mapped[str] = mapped_column(unique=True)
    range: Mapped[int] = mapped_column(default=0)
    attacks: Mapped[str] = mapped_column(default="1")
    weapon_skill: Mapped[str] = mapped_column(default=1)
    strength: Mapped[int] = mapped_column(default=1)
    armour_penetration: Mapped[int] = mapped_column(default=0)
    damage: Mapped[int] = mapped_column(default=1)
    rapid_fire: Mapped[int] = mapped_column(default=0)
    anti_infantry: Mapped[str] = mapped_column(default="")
    devastating_wounds: Mapped[bool] = mapped_column(default=False)

    units: Mapped[list["Unit"]] = relationship("Unit", secondary=unit_weapon_association, back_populates="weapons", default_factory=list)
    id: Mapped[int|None] = mapped_column(primary_key=True, autoincrement=True, default=None, nullable=False)

    def __init__(self, *args, **kwargs):
        """ Override to handle unit_ids parameter """
        units = [db.session.get(Unit, u_id) for u_id in kwargs.pop("unit_ids", [])]
        return super().__init__(*args, units=units, **kwargs)
