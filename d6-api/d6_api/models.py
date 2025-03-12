from flask_alembic import Alembic
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import Mapped, mapped_column

from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy import MetaData

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

db = SQLAlchemy(model_class=Model)
al = Alembic(metadatas=Model.metadata)


class Unit(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)

