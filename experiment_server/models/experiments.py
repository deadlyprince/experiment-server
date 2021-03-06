""" This is a database-schema """
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Text,
    DateTime
)

import datetime
from sqlalchemy.orm import relationship
from experiment_server.models.meta import Base

class Experiment(Base):
    """
    This is definition of class Experiment.
    Experiment-object defines how long an experiment on Application is being run. On same Experiment, many
    ExperimentGroups can be set.
    """
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True)
    application_id = Column(Integer, ForeignKey('applications.id'))
    name = Column(Text, unique=True, index=True, nullable=False)
    startDatetime = Column(DateTime)
    endDatetime = Column(DateTime)
    experimentgroups = relationship("ExperimentGroup", backref="experiment", cascade="delete")

    def as_dict(self):
        result = {}
        for c in self.__table__.columns:
            if c.name == 'startDatetime' or c.name == 'endDatetime':
                result[c.name] = str(getattr(self, c.name))
            else:
                result[c.name] = getattr(self, c.name)
        return result

    def get_status(self):
        """
        get status of the experiment by comparing start datetime and end
        datetime.
        Return:
            None, if start- and end times are incorrectly set
            'running' if current date is between start- and end time
            'finished' if current date is after end time
            'waiting' if current date is before start time
        """
        # open = 'open'
        running = 'running'
        finished = 'finished'
        waiting = 'waiting'

        date_time_now = datetime.datetime.now()
        start_datetime = self.startDatetime
        end_datetime = self.endDatetime
        if start_datetime >= end_datetime:
            # validate this earlier
            return None
        if start_datetime <= date_time_now and date_time_now <= end_datetime:
            return running
        elif date_time_now > end_datetime:
            return finished
        elif date_time_now < start_datetime:
            return waiting
        return None
