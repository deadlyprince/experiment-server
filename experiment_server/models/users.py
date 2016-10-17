""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    Text,
)

from sqlalchemy.orm import relationship

from .meta import Base
from .users_experimentgroups import users_experimentgroups


class User(Base):
    """ This is definition of class User. """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(Text, unique=True, index=True)
    dataitems = relationship("DataItem", backref="user", cascade="delete")
    experimentgroups = relationship(
        "ExperimentGroup",
        secondary=users_experimentgroups,
        back_populates="users"
    )

    def as_dict(self):
        """ Transfer data to dictionary """
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
