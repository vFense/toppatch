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
    id = Column(BIGINT(unsigned=True),primary_key=True, autoincrement=True)
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


class SoftwareInstalled(Base):
    """
    Represents an application that is installed on a node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "software_installed"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=True )
    node_id = Column(BIGINT(unsigned=True),ForeignKey("node_info.id"))
    name = Column(VARCHAR(128),nullable=False)
    vendor_id = Column(BIGINT(unsigned=True))
    description = Column(VARCHAR(128), nullable=True)
    support_url = Column(VARCHAR(128), nullable=True)
    operating_system = Column(VARCHAR(32), nullable=False)
    version = Column(VARCHAR(32), nullable=False)
    vendor = Column(VARCHAR(32), nullable=False)
    date_installed = Column(DATETIME, nullable=True)
    def __init__(self, name, vendor, vendor_id, description, operating_system, version, support_url=None, date_installed=None):
        self.name = name
        self.vendor = vendor
        self.vendor_id = vendor_id
        self.description = description
        self.operating_system = operating_system
        self.version = version
        self.support_url = support_url
        self.date_installed = date_installed
    def __repr__(self):
        return "<SoftwareInstalled(%s, %s, %s, %s, %s, %s, %s, %s)>" %(self.name, self.vendor, self.vendor_id, self.description, self.operating_system, self.version, self.support_url, self.date_installed)
