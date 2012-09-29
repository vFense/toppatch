#!/usr/bin/env python                                                                                                                                                     
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref

class SslInfo(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "ssl_info"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),ForeignKey("node_info.id"))
    csr_id = Column(INTEGER(unsigned=True),ForeignKey("csr.id"))
    signed_cert_name = Column(VARCHAR(128),nullable=False)
    signed_cert_location = Column(VARCHAR(128),nullable=False)
    cert_expiration = Column(DATETIME, nullable=True)
    def __init__(self, node_id, csr_id,
                signed_cert_name, signed_cert_location,
                cert_expiration
                ):
        self.node_id = node_id
        self.csr_id = csr_id
        self.signed_cert_name = signed_cert_name
        self.signed_cert_location = signed_cert_location
        self.cert_expiration = cert_expiration
    def __repr__(self):
        return "<SslInfo(%s,%s,%s,%s,%s)>" %\
                (
                self.node_id, self.csr_id,
                self.signed_cert_name, self.signed_cert_location,
                self.cert_expiration
                )

class CsrInfo(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "csr_info"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    csr_name = Column(VARCHAR(128),nullable=False)
    ip_address = Column(VARCHAR(16),nullable=False)
    csr_location = Column(VARCHAR(128),nullable=False)
    is_csr_signed = Column(BOOLEAN, nullable=True)
    csr_signed_date = Column(DATETIME, nullable=True)
    def __init__(self, csr_name, ip_address,
                csr_location, is_csr_signed,
                csr_signed_date
                ):
        self.csr_name = csr_name
        self.ip_address = ip_address
        self.csr_location = csr_location
        self.is_csr_signed = is_csr_signed
        self.csr_signed_date = csr_signed_date
    def __repr__(self):
        return "<CsrInfo(%s,%s,%s,%s,%s)>" %\
                (
                self.csr_name, self.ip_address,
                self.csr_location, self.is_csr_signed,
                self.csr_signed_date
                )

