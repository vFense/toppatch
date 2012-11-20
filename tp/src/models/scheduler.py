#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref


class TimeBlocker(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "time_blocker"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    name = Column(VARCHAR(1024), nullable=False)
    enabled = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    start_date = Column(DATETIME, nullable=False)
    end_date = Column(DATETIME, nullable=True)
    start_time = Column(TIME, nullable=False)
    end_time = Column(TIME, nullable=False)
    days = Column(VARCHAR(7), nullable=False)
    def __init__(self, name, start_date, end_date,
                start_time, end_time, days, 
                enabled=True
                ):
        self.name = name
        self.enabled = enabled
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.days = days
    def __repr__(self):
        return "<TimeBlocker(%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.name, self.enabled, self.start_date,
                self.end_date, self.start_time,
                self.end_time, self.days,
                )
