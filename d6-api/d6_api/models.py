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

    def to_table_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def to_dict(self):
        attributes = self.to_table_dict()
        relationships = inspect(self).relationships.keys()
        for r_name in relationships:
            attributes[r_name] = getattr(self, r_name).to_table_dict()
        return attributes


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


class Unit(db.Model):
    name: Mapped[str] = mapped_column(unique=True)
    toughness: Mapped[int] = mapped_column()
    save: Mapped[str] = mapped_column()
    weapons: Mapped[list["Weapon"]] = relationship("Weapon", secondary=unit_weapon_association, back_populates="units", default_factory=list)
    id: Mapped[int|None] = mapped_column(primary_key=True, autoincrement=True, default=None)


class Weapon(db.Model):
    name: Mapped[str] = mapped_column(unique=True)
    weapon_skill: Mapped[str] = mapped_column()
    strength: Mapped[int] = mapped_column()
    attacks: Mapped[int] = mapped_column(default=1)
    armour_penetration: Mapped[int] = mapped_column(default=0)
    units: Mapped[list["Unit"]] = relationship("Unit", secondary=unit_weapon_association, back_populates="weapons", default_factory=list)
    id: Mapped[int|None] = mapped_column(primary_key=True, autoincrement=True, default=None)

