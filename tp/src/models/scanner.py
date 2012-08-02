"""
Models classes that store data from the scanner.

ALL DATA COMES FROM THE SCANNER
"""

from models.base import Base

from sqlalchemy import String, Integer, Boolean, Column, Date, Time, ForeignKey
from sqlalchemy.orm import relationship, backref

class Node(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(32))
    host_name = Column(String(32))
    snmp_status = Column(Boolean)   # True = On, False = Off
    host_status = Column(Boolean)   # True = On, False = Off

    installed_apps = relationship("NodeApp", backref="node")

    def __init__(self, ip_address, host_name, host_status=False, snmp_status=False):
        self.ip_address = ip_address
        self.host_name = host_name
        self.host_status = host_status
        self.snmp_status = snmp_status

class NodeApp(Base):
    """
    Represents an application that is installed on a node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "node_apps"

    id = Column(Integer, primary_key=True)
    port = Column(Integer)
    protocol = Column(String(12))
    last_scan_date = Column(Date)
    last_scan_time = Column(Time)

    app_id = Column(Integer, ForeignKey('apps_list.id'))
    node_id = Column(Integer, ForeignKey('nodes.id'))

    def __init__(self, port, protocol, last_scan_date, last_scan_time):
        self.port = port
        self.protocol = protocol
        self.last_scan_date = last_scan_date
        self.last_scan_time = last_scan_time

class App(Base):
    """ Table of all the apps installed of each node on the network.
    Contains app name and version.
    """
    __tablename__ = "apps_list"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    version = Column(String(255))

    installed_apps = relationship("NodeApp", backref="app")

    def __init__(self, name, version):
        self.name = name
        self.version = version

