#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import BIGINT, BOOLEAN, CHAR, DATETIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref


class NodeInfo(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "node_info"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(BIGINT(unsigned=True),primary_key=True)
    host_name = Column(VARCHAR(32), nullable=False)
    ip_address = Column(VARCHAR(16), nullable=False)
    operating_system = Column(VARCHAR(32), nullable=False)
    os_version = Column(VARCHAR(32), nullable=False)
    host_status = Column(BOOLEAN)   # True = On, False = Off
    def __init__(self, ip_address, host_name, operating_system,os_version, host_status=False):
        self.host_name = host_name
        self.ip_address = ip_address
        self.operating_system = operating_system
        self.os_version = os_version
        self.host_status = host_status
    def __repr__(self):
        return "<NodeInfo(%s, %s, %s, %s, %s)>" %(self.host_name, self.ip_address, self.operating_system,self.os_version, self.host_status)

