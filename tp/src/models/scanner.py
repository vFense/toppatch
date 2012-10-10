"""
Models classes that store data from the scanner.

ALL DATA COMES FROM THE SCANNER
"""

from models.base import Base
from models.application import Product, Version

from sqlalchemy import String, Integer, Boolean, Column, Date, Time, ForeignKey
from sqlalchemy.orm import relationship

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

    def __repr__(self):
        return "<Node(%s, %s)>" % (self.ip_address, self.host_name)

class NodeApp(Base):
    """
    Represents an application that is installed on a node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "node_apps"

    id = Column(Integer, primary_key=True)
    port = Column(Integer)
    protocol = Column(String(12))
    last_scan_date = Column(Date)

    app_id = Column(Integer, ForeignKey('apps_list.id'))
    node_id = Column(Integer, ForeignKey('nodes.id'))

    def __init__(self, port, protocol, last_scan_date):
        self.port = port
        self.protocol = protocol
        self.last_scan_date = last_scan_date

    def __repr__(self):
        return "<NodeApp(%s, %s)>" % (self.app, self.node)

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

    def __repr__(self):
        return "<App(%s, %s)>" % (self.name, self.version)

class Vulnerability(Base):
    """ Represents one row from the 'vulnerabilities' table.

    Latest known vulnerability in the network. Once the client server compares the CVE data and the scanned apps of each
    node, the results are stored here.

    One vulnerability contains:

        - application affected
        - application version
        - CVE (which in turn can access the refs, score, etc)
        - node it belongs to (ip address and/or hostname)
        - fixed status(whether or not the vulnerability has been resolved. True or False)

        - date found - date which the vulnerability was first discovered on this node.
        - date fixed - date which the vulnerability was resolved.
    """
    __tablename__ = "vulnerabilities"

    id = Column(Integer, primary_key=True)
    fixed = Column(Boolean)
    
    node = relationship("Node", uselist=False)
    product = relationship("Product", uselist=False)
    version = relationship("Version", uselist=False)

    product_id = Column(Integer, ForeignKey("products.id"))
    version_id = Column(Integer, ForeignKey("versions.id"))

    node_id = Column(Integer, ForeignKey("nodes.id"))

    def __init__(self, product, version, node, fixed=False):

        self.product_id = product.id
        self.version_id = version.id
        self.node_id = node.id

        self.fixed = fixed

    def __repr__(self):
        return "<Vulnerability('Fixed: %s')>" % (self.fixed)

