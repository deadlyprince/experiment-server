""" This is a schema """
from sqlalchemy import (
    Column,
    Integer,
    Text
)

from sqlalchemy.orm import relationship
from .meta import Base


class Operator(Base):
    """ This is definition of operator class """
    __tablename__ = 'operators'
    id = Column(Integer, primary_key=True)
    math_value = Column(Text)
    human_value = Column(Text)
    rangeconstraints = relationship("RangeConstraint", backref="operator", cascade="delete")