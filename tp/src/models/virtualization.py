#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref


class VirtualHostInfo(Base):
    """
        This table contains the base information of a node in RV
        
    """
    __tablename__ = "virtual_host_info"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    name = Column(VARCHAR(64), nullable=True, unique=True)
    ip_address = Column(VARCHAR(16), nullable=True, unique=True)
    version = Column(VARCHAR(64), nullable=True, unique=True)
    virt_type = Column(VARCHAR(64), nullable=True, unique=True)
    def __init__(self, name=None, ip_address=None, version=None,
                virt_type=None
                ):
        self.name = name
        self.ip_address = ip_address
        self.version = version
        self.virt_type = virt_type
    def __repr__(self):
        return "<VirtualHostInfo(%s,%s,%s,%s)>" %\
                (
                self.name, self.ip_address, self.version,
                self.virt_type
                )


class VirtualMachineInfo(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "virtual_machine_info"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),
            ForeignKey("node_info.id"), unique=True)
    virtual_host_id = Column(INTEGER(unsigned=True),
            ForeignKey("virtual_host_info.id"), unique=False)
    vm_name = Column(VARCHAR(128), nullable=True, unique=True)
    uuid = Column(VARCHAR(64), nullable=True, unique=True)
    tools_status = Column(VARCHAR(64), nullable=False)
    tools_version = Column(VARCHAR(64), nullable=False)
    def __init__(
                self, node_id=None, virtual_host_id=None, vm_name=None,
                uuid=None, tools_status=None, tools_version=None
                ):
        self.node_id = node_id
        self.virtual_host_id = virtual_host_id
        self.vm_name = vm_name
        self.uuid = uuid
        self.tools_status = tools_status
        self.tools_version = tools_version
    def __repr__(self):
        return "<VirtualMachineInfo(%s%s,%s,%s,%s,%s)>"%\
                (
                self.node_id, self.virtual_host_id, self.vm_name,
                self.uuid, self.tools_status, self.tools_version
                )
