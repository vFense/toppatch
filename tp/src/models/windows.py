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

class WindowsUpdate(Base):
    """
    Represents an application that is installed on a node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "windows_update"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    toppatch_id = Column(BIGINT(unsigned=True), primary_key=True, autoincrement=False )
    vendor_id = Column(BIGINT(unsigned=True))
    title = Column(VARCHAR(128),nullable=False)
    description = Column(VARCHAR(128), nullable=False)
    support_url = Column(VARCHAR(128), nullable=False)
    severity = Column(VARCHAR(16), nullable=False)
    date_pub = Column(DATETIME)
    def __init__(self, toppatch_id, vendor_id, title, description,support_url, severity, date_pub):
        self.toppatch_id = toppatch_id
        self.vendor_id = vendor_id
        self.title = title
        self.description = description
        self.support_url = support_url
        self.severity = severity
        self.date_pub = date_pub
    def __repr__(self):
        return "<WindowsUpdate(%s, %s, %s, %s, %s, %s, %s)>" %(self.toppatch_id, self.vendor_id, self.title,self.description, self.support_url,self.severity, self.date_pub)

class ManagedWindowsUpdate(Base):
    """
    Represents an application that is installed on a node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "managed_windows_update"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(BIGINT(unsigned=True), primary_key=True)
    node_id = Column(BIGINT(unsigned=True),ForeignKey("node_info.id"))
    toppatch_id = Column(BIGINT(unsigned=True),ForeignKey("windows_update.toppatch_id"))
    hidden = Column(BOOLEAN)
    installed = Column(BOOLEAN)
    date_installed = Column(DATETIME)
    def __init__(self, date_installed, hidden=False, installed=False):
        self.date_installed = date_installed
        self.hidden = hidden
        self.installed = installed
    def __repr__(self):
        return "<ManagedWindowsUpdate(%s, %s, %s, %s, %s, %s)>" %(self.toppatch_id, self.id, self.node_id,self.hidden, self.installed,self.date_installed)

