#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref


class SnapshotsPerNode(Base):
    """
        This table contains the base information of a node in RV
        
    """
    __tablename__ = "snapshot_per_node"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),ForeignKey("node_info.id"), unique=False)
    name = Column(VARCHAR(256), nullable=False, unique=False)
    description = Column(VARCHAR(256), nullable=True, unique=False)
    order = Column(INTEGER)
    created_time = Column(DATETIME, nullable=False)
    def __init__(self, node_id=None, name=None, description=None,
            order=None, created_time=None):
        self.node_id = node_id
        self.name = name
        self.description = description
        self.order = order
        self.created_time = created_time
    def __repr__(self):
        return "<SnapshotsPerNode(%s,%s,%s,%s,%S)>" %\
                (self.node_id, self.name, self.description,
                self.order, self.created_time)
