"""
Models classes that store data from the scanner.
"""

from base import Base

from sqlalchemy import String, Integer, Boolean, Column, Text, ForeignKey
from sqlalchemy.orm import relationship, backref

class Host(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "hosts"

    id = Column(Integer, primary_key=True)
    ip_address = Column(String(32))
    host_name = Column(String(32))
    snmp_status = Column(Boolean)   # True = On, False = Off
    host_status = Column(Boolean)   # True = On, False = Off

    client_apps = relationship("ClientApp", backref="hosts")

    def __init__(self, ip_address, host_name, host_status=False, snmp_status=False):
        self.ip_address = ip_address
        self.host_name = host_name
        self.host_status = host_status
        self.snmp_status = snmp_status

class ClientApp(Base):
    """
    Represents an application that is installed on a client node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "client_apps"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    version = Column(String(32))
    port = Column(Integer)
    protocol = Column(String(12))

    host_id = Column(Integer, ForeignKey('hosts.id'))

    def __init__(self, name, version, port, protocol ):
        self.name = name
        self.version = version
        self.port = port
        self.protocol = protocol

