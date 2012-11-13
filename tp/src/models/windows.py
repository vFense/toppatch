#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref


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
    toppatch_id = Column(VARCHAR(32),
        primary_key=True, unique=True, nullable=False
    )
    kb = Column(VARCHAR(32), nullable=False)
    vendor_id = Column(VARCHAR(128), nullable=False)
    title = Column(VARCHAR(1024),nullable=False)
    description = Column(VARCHAR(4098), nullable=True)
    support_url = Column(VARCHAR(128), nullable=True)
    severity = Column(VARCHAR(16), nullable=False)
    date_pub = Column(DATETIME)
    file_size = Column(INTEGER(unsigned=True), nullable=False)
    def __init__(
            self, toppatch_id, kb, vendor_id, title,
            description,support_url, severity, date_pub,
            file_size
    ):
        self.toppatch_id = toppatch_id
        self.kb = kb
        self.vendor_id = vendor_id
        self.title = title
        self.description = description
        self.support_url = support_url
        self.severity = severity
        self.date_pub = date_pub
        self.file_size = file_size
    def __repr__(self):
        return "<WindowsUpdate(%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
               (
                   self.toppatch_id, self.kb, self.vendor_id,
                   self.title, self.description, self.support_url,
                   self.severity, self.date_pub, self.file_size
                   )

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
    id = Column(INTEGER(unsigned=True),
        primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),
        ForeignKey("node_info.id"))
    toppatch_id = Column(VARCHAR(32),
        ForeignKey("windows_update.toppatch_id"))
    hidden = Column(BOOLEAN)
    installed = Column(BOOLEAN)
    attempts = Column(INTEGER)
    pending = Column(BOOLEAN)
    date_installed = Column(DATETIME)
    def __init__(self, node_id, toppatch_id, date_installed=None,
                 hidden=False, installed=False, attempts=0,
                 pending=False
    ):
        self.node_id = node_id
        self.toppatch_id = toppatch_id
        self.hidden = hidden
        self.installed = installed
        self.date_installed = date_installed
        self.attempts = attempts
        self.pending = pending
    def __repr__(self):
        return "<ManagedWindowsUpdate(%s,%s,%s,%s,%s,%s,%s)>" %\
               (
                   self.node_id, self.toppatch_id, self.hidden,
                   self.installed, self.date_installed, self.attempts,
                   self.pending
                   )
