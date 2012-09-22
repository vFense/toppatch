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
    os_code = Column(VARCHAR(16), nullable=False)
    os_string = Column(VARCHAR(32), nullable=False)
    os_version_major = Column(VARCHAR(6), nullable=False)
    os_version_minor = Column(VARCHAR(6), nullable=True)
    os_version_build = Column(VARCHAR(8), nullable=True)
    os_meta = Column(VARCHAR(32), nullable=True)
    host_status = Column(BOOLEAN)   # True = Up, False = Down
    agent_status = Column(BOOLEAN)   # True = Up, False = Down
    last_agent_update = Column(DATETIME, nullable=False)
    last_node_update = Column(DATETIME, nullable=False)
    def __init__(self, ip_address, host_name, os_code,
            os_string, os_version_major, os_version_minor,
            os_version_build, os_meta, host_status=False,
            agent_status=False, last_agent_update=None,
            last_node_update=None
            ):
        self.host_name = host_name
        self.ip_address = ip_address
        self.os_code = os_code
        self.os_string = os_string
        self.os_version_major = os_version_major
        self.os_version_minor = os_version_minor
        self.os_version_build = os_version_build
        self.os_meta = os_meta
        self.host_status = host_status
        self.agent_status = agent_status
        self.last_agent_update = last_agent_update
        self.last_node_update = last_node_update
    def __repr__(self):
        return "<NodeInfo(%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                id, self.host_name, self.ip_address,
                self.os_code, self.os_string, self.os_version_major,
                self.os_version_minor, self.os_version_build,
                self.os_meta, self.host_status, self.agent_status,
                self.last_agent_update, self.last_node_update
                )

class Operations(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "operations"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(BIGINT(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(BIGINT(unsigned=True),ForeignKey("node_info.id"))
    results_id = Column(BIGINT(unsigned=True),
        ForeignKey("results.id", use_alter=True,
        name="fk_operations_result_id"))
    operation_type = Column(VARCHAR(16), nullable=False)
    operation_sent = Column(DATETIME, nullable=True)
    operation_received = Column(DATETIME, nullable=True)
    def __init__(self, operation_type,
            operation_sent=None,
            operation_received=None
            ):
        self.operation = operation
        self.node_name = node_name
        self.operation_sent = operation_sent
        self.operation_received = operation_received
    def __repr__(self):
        return "<Operations(%d, %s, %s, %s, %s,)>" %\
                (
                id, node_id, results_id, self.operation_type, 
                self.operation_sent,self.operation_received
                )

class Results(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "results"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(BIGINT(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(BIGINT(unsigned=True),ForeignKey("node_info.id"))
    operation_id = Column(BIGINT(unsigned=True),ForeignKey("operations.id"))
    patch_id = Column(BIGINT(unsigned=True),
        ForeignKey("windows_update.toppatch_id", use_alter=True,
        name="fk_result_operations_id"))
    result = Column(BOOLEAN)   # True = Pass, False = Failed
    message = Column(VARCHAR(64), nullable=True)
    def __init__(self, result, message):
        self.result = result
        self.message = message
    def __repr__(self):
        return "<Results(%d, %d, %d, %d, %s, %s)>" %\
                (
                id, node_id ,operation_id, patch_id,
                self.result, self.message
                )

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
        return "<SoftwareInstalled(%d,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                node_id, self.name, self.vendor, self.vendor_id,
                self.description, self.operating_system,
                self.version, self.support_url,
                self.date_installed
                )
