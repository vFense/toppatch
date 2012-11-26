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
    start_date = Column(DATETIME, nullable=False)
    start_time = Column(TIME, nullable=False)
    end_date = Column(DATETIME, nullable=True)
    end_time = Column(TIME, nullable=False)
    span_end_date_time = Column(DATETIME, nullable=True)
    days = Column(VARCHAR(7), nullable=False)
    span = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    enabled = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    def __init__(self, name, start_date, start_time, end_time, days,
                end_date=None, span_end_date_time=None, span=False,
                enabled=True
                ):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.start_time = start_time
        self.end_time = end_time
        self.span_end_date_time = span_end_date_time
        self.days = days
        self.span = span
        self.enabled = enabled
    def __repr__(self):
        return "<TimeBlocker(%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.name, self.start_date, self.start_time,
                self.end_date, self.end_time, self.span_end_date_time,
                self.span, self.days, self.enabled
                )
