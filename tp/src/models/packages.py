#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref

class Package(Base):
    """
    Represents an application that is installed on a node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "package"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    toppatch_id = Column(VARCHAR(32),
        primary_key=True, unique=True, nullable=False
    )
    version = Column(VARCHAR(32), nullable=True)
    kb = Column(VARCHAR(32), nullable=True)
    vendor_id = Column(VARCHAR(128), nullable=False)
    name = Column(VARCHAR(1024),nullable=False)
    description = Column(VARCHAR(4098), nullable=True)
    support_url = Column(VARCHAR(128), nullable=True)
    severity = Column(VARCHAR(16), nullable=True)
    date_pub = Column(DATETIME)
    file_size = Column(INTEGER(unsigned=True), nullable=False)
    def __init__(
            self, toppatch_id, version, kb, vendor_id, name,
            description, support_url, severity, date_pub,
            file_size
    ):
        self.toppatch_id = toppatch_id
        self.version = version
        self.vendor_id = vendor_id
        self.kb = kb
        self.name = name
        self.description = description
        self.support_url = support_url
        self.severity = severity
        self.date_pub = date_pub
        self.file_size = file_size
    def __repr__(self):
        return "<LinuxPackage(%r,%r,%r,%r,%r,%r,%r,%r,%r,%r)>" %\
               (
                   self.toppatch_id, self.version, self.vendor_id,
                   self.kb, self.name, self.description, self.support_url,
                   self.severity, self.date_pub, self.file_size
                   )

class PackagePerNode(Base):
    """
    Represents an application that is installed on a node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "package_per_node"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),
        primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),
        ForeignKey("node_info.id"))
    toppatch_id = Column(VARCHAR(32),
        ForeignKey("package.toppatch_id"))
    is_linux = Column(BOOLEAN, nullable=True)
    is_windows = Column(BOOLEAN, nullable=True)
    is_darwin = Column(BOOLEAN, nullable=True)
    is_bsd = Column(BOOLEAN, nullable=True)
    is_unix = Column(BOOLEAN, nullable=True)
    hidden = Column(BOOLEAN)
    installed = Column(BOOLEAN)
    attempts = Column(INTEGER)
    pending = Column(BOOLEAN)
    date_installed = Column(DATETIME)
    def __init__(self, node_id, toppatch_id, date_installed=None,
                 hidden=False, installed=False, attempts=0,
                 pending=False, is_linux=False, is_windows=False,
                 is_darwin=False, is_bsd=False, is_unix=False
                ):
        self.node_id = node_id
        self.toppatch_id = toppatch_id
        self.is_linux = is_linux
        self.is_windows = is_windows
        self.is_darwin = is_darwin
        self.is_bsd = is_bsd
        self.is_unix = is_unix
        self.hidden = hidden
        self.installed = installed
        self.date_installed = date_installed
        self.attempts = attempts
        self.pending = pending
    def __repr__(self):
        return "<PackagePerNode(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
               (
                   self.node_id, self.toppatch_id, self.is_linux,
                   self.is_windows, self.is_darwin, self.is_bsd, self.is_unix,
                   self.hidden, self.installed, self.date_installed,
                   self.attempts,self.pending
                   )

class PackageDependency(Base):
    """
    Represents an application that is installed on a node, as oppose to a Product from a Vendor in the database.
    """
    __tablename__ = "package_dependency"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),
        primary_key=True, autoincrement=True)
    toppatch_id = Column(VARCHAR(32),
        ForeignKey("package.toppatch_id"))
    dependency = Column(VARCHAR(32),
        ForeignKey("package.toppatch_id"))
    def __init__(self, toppatch_id, dependency):
        self.toppatch_id = toppatch_id
        self.dependency = dependency
    def __repr__(self):
        return "<PackageDependency(%s,%s)>" %\
               (
                self.toppatch_id, self.dependency,
               )
