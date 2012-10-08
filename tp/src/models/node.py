#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TEXT, TINYINT, VARCHAR
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
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    host_name = Column(VARCHAR(32), nullable=True, unique=True)
    ip_address = Column(VARCHAR(16), nullable=False, unique=True)
    host_status = Column(BOOLEAN, nullable=True)   # True = Up, False = Down
    agent_status = Column(BOOLEAN, nullable=True)   # True = Up, False = Down
    last_agent_update = Column(DATETIME, nullable=True)
    last_node_update = Column(DATETIME, nullable=True)
    def __init__(self, ip_address, host_name,
                host_status=False, agent_status=False,
                last_agent_update=None, last_node_update=None
                ):
        self.host_name = host_name
        self.ip_address = ip_address
        self.host_status = host_status
        self.agent_status = agent_status
        self.last_agent_update = last_agent_update
        self.last_node_update = last_node_update
    def __repr__(self):
        return "<NodeInfo(%s,%s,%s,%s,%s,%s)>" %\
                (
                self.host_name, self.ip_address,
                self.host_status, self.agent_status,
                self.last_agent_update, self.last_node_update
                )

class SystemInfo(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "system_info"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),ForeignKey("node_info.id"), unique=True)
    os_code = Column(VARCHAR(16), nullable=False)
    os_string = Column(VARCHAR(32), nullable=False)
    bit_type = Column(VARCHAR(4), nullable=False)
    os_version_major = Column(VARCHAR(6), nullable=True)
    os_version_minor = Column(VARCHAR(6), nullable=True)
    os_version_build = Column(VARCHAR(8), nullable=True)
    os_meta = Column(VARCHAR(32), nullable=True)
    def __init__(
                self, node_id, os_code, os_string, bit_type,
                os_version_major, os_version_minor,
                os_version_build, os_meta
                ):
        self.node_id = node_id
        self.os_code = os_code
        self.os_string = os_string
        self.bit_type = bit_type
        self.os_version_major = os_version_major
        self.os_version_minor = os_version_minor
        self.os_version_build = os_version_build
        self.os_meta = os_meta
    def __repr__(self):
        return "<SystemInfo(%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.node_id, self.os_code, self.os_string, self.bit_type
                self.os_version_major, self.os_version_minor,
                self.os_version_build, self.os_meta
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
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),
        ForeignKey("node_info.id"))
    results_id = Column(INTEGER(unsigned=True),
        ForeignKey("results.id", use_alter=True,
        name="fk_operations_result_id"))
    operation_type = Column(VARCHAR(16), nullable=False)
    operation_sent = Column(DATETIME, nullable=True)
    operation_received = Column(DATETIME, nullable=True)
    results_received = Column(DATETIME, nullable=True)
    def __init__(self, node_id, operation_type, results_id=None,
            operation_sent=None, operation_received=None,
            results_received=None
            ):
        self.node_id = node_id
        self.results_id = results_id
        self.operation_type = operation_type
        self.operation_sent = operation_sent
        self.operation_received = operation_received
        self.results_received = results_received
    def __repr__(self):
        return "<Operations(%s, %s, %s, %s, %s,%s)>" %\
                (
                self.node_id, self.results_id, self.operation_type, 
                self.operation_sent,self.operation_received,
                self.results_received
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
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),ForeignKey("node_info.id"))
    operation_id = Column(INTEGER(unsigned=True),
        ForeignKey("operations.id", use_alter=True,
        name="fk_result_operations_id"),unique=True)
    patch_id = Column(INTEGER(unsigned=True),
        ForeignKey("windows_update.toppatch_id"))
    result = Column(BOOLEAN)   # True = Pass, False = Failed
    message = Column(VARCHAR(64), nullable=True)
    def __init__(self, node_id, operation_id, patch_id,
                result, message):
        self.node_id = node_id
        self.operation_id = operation_id
        self.patch_id = patch_id
        self.result = result
        self.message = message
    def __repr__(self):
        return "<Results(%s, %s, %s, %s, %s)>" %\
                (
                self.node_id ,self.operation_id, self.patch_id,
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
    id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True )
    node_id = Column(INTEGER(unsigned=True),ForeignKey("node_info.id"))
    name = Column(VARCHAR(128),nullable=False)
    description = Column(VARCHAR(128), nullable=True)
    support_url = Column(VARCHAR(128), nullable=True)
    version = Column(VARCHAR(32), nullable=False)
    vendor = Column(VARCHAR(32), nullable=False)
    date_installed = Column(DATETIME, nullable=True)
    def __init__(self, node_id, name, vendor,
                description, version,
                support_url=None, date_installed=None):
        self.node_id = node_id
        self.name = name
        self.vendor = vendor
        self.description = description
        self.version = version
        self.support_url = support_url
        self.date_installed = date_installed
    def __repr__(self):
        return "<SoftwareInstalled(%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.node_id, self.name, self.vendor,
                self.description, self.version,
                self.support_url, self.date_installed
                )


class NodeStats(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "node_stats"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),ForeignKey("node_info.id"))
    patches_installed = Column(INTEGER(unsigned=True))
    patches_available = Column(INTEGER(unsigned=True))
    patches_pending = Column(INTEGER(unsigned=True))
    patches_failed = Column(INTEGER(unsigned=True))
    def __init__(self, node_id, patches_installed,
                patches_available, patches_pending,
                patches_failed
                ):
        self.node_id = node_id
        self.patches_installed = patches_installed
        self.patches_available = patches_available
        self.patches_pending = patches_pending
        self.patches_failed = patches_failed
    def __repr__(self):
        return "<NodeStats(%d,%d,%d,%d,%d)>" %\
                (
                self.node_id, self.patches_installed,
                self.patches_available, self.patches_pending,
                self.patches_failed
                )

class NetworkStats(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "network_stats"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    patches_installed = Column(INTEGER(unsigned=True))
    patches_available = Column(INTEGER(unsigned=True))
    patches_pending = Column(INTEGER(unsigned=True))
    patches_failed = Column(INTEGER(unsigned=True))
    def __init__(self, patches_installed,
                patches_available, patches_pending,
                patches_failed
                ):
        self.patches_installed = patches_installed
        self.patches_available = patches_available
        self.patches_pending = patches_pending
        self.patches_failed = patches_failed
    def __repr__(self):
        return "<NetworkStats(%d,%d,%d,%d)>" %\
                (
                self.patches_installed,
                self.patches_available, self.patches_pending,
                self.patches_failed
                )
