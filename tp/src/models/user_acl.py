#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref

class GlobalUserAccess(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "global_user_access"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    is_admin = Column(BOOLEAN, nullable=False)         # True = Up, False = Down
    is_global = Column(BOOLEAN, nullable=False)         # True = Up, False = Down
    read_only = Column(BOOLEAN, nullable=False)          # True = Up, False = Down
    allow_install = Column(BOOLEAN, nullable=False)       # True = Up, False = Down
    allow_uninstall = Column(BOOLEAN, nullable=False)      # True = Up, False = Down
    allow_reboot = Column(BOOLEAN, nullable=False)          # True = Up, False = Down
    allow_schedule = Column(BOOLEAN, nullable=False)         # True = Up, False = Down
    allow_wol = Column(BOOLEAN, nullable=False)               # True = Up, False = Down
    allow_snapshot_creation = Column(BOOLEAN, nullable=False) # True = Up, False = Down
    allow_snapshot_removal = Column(BOOLEAN, nullable=False) # True = Up, False = Down
    allow_snapshot_revert = Column(BOOLEAN, nullable=False) # True = Up, False = Down
    allow_tag_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    deny_all = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    date_created = Column(DATETIME, nullable=True)
    date_modified = Column(DATETIME, nullable=True)
    def __init__(self, user_id=None, is_admin=False, is_global=True,
            read_only=False, allow_install=False, allow_uninstall=False,
            allow_reboot=False, allow_schedule=False, allow_wol=False,
            allow_snapshot_creation=False, allow_snapshot_removal=False,
            allow_snapshot_revert=False, allow_tag_creation=False,
            allow_tag_removal=False, deny_all=False, date_created=None,
            date_modified=None
            ):
        self.user_id = user_id
        self.is_admin = is_admin
        self.is_global = is_global
        self.read_only = read_only
        self.allow_install = allow_install
        self.allow_uninstall = allow_uninstall
        self.allow_reboot = allow_reboot
        self.allow_schedule = allow_schedule
        self.allow_wol = allow_wol
        self.allow_snapshot_creation = allow_snapshot_creation
        self.allow_snapshot_removal = allow_snapshot_removal
        self.allow_snapshot_revert = allow_snapshot_revert
        self.allow_tag_creation = allow_tag_creation
        self.allow_tag_removal = allow_tag_removal
        self.deny_all = deny_all
        self.date_created = date_created
        self.date_modified = date_modified
    def __repr__(self):
        return "<GlobalUserAccess(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.user_id, self.is_admin, self.is_global,
                self.read_only, self.allow_install, self.allow_uninstall,
                self.allow_reboot, self.allow_schedule, self.allow_wol,
                self.allow_snapshot_creation, self.allow_snapshot_removal,
                self.allow_snapshot_revert, self.allow_tag_creation,
                self.allow_tag_removal, self.deny_all, self.date_created,
                self.date_modified
                )


class GlobalGroupAccess(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "global_group_access"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    group_id = Column(INTEGER, ForeignKey('groups.id'), unique=True)
    is_admin = Column(BOOLEAN, nullable=False)         # True = Up, False = Down
    is_global = Column(BOOLEAN, nullable=False)         # True = Up, False = Down
    read_only = Column(BOOLEAN, nullable=False)          # True = Up, False = Down
    allow_install = Column(BOOLEAN, nullable=False)       # True = Up, False = Down
    allow_uninstall = Column(BOOLEAN, nullable=False)      # True = Up, False = Down
    allow_reboot = Column(BOOLEAN, nullable=False)          # True = Up, False = Down
    allow_schedule = Column(BOOLEAN, nullable=False)         # True = Up, False = Down
    allow_wol = Column(BOOLEAN, nullable=False)               # True = Up, False = Down
    allow_snapshot_creation = Column(BOOLEAN, nullable=False) # True = Up, False = Down
    allow_snapshot_removal = Column(BOOLEAN, nullable=False) # True = Up, False = Down
    allow_snapshot_revert = Column(BOOLEAN, nullable=False) # True = Up, False = Down
    allow_tag_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    deny_all = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    date_created = Column(DATETIME, nullable=True)
    date_modified = Column(DATETIME, nullable=True)
    def __init__(self, group_id=None, is_admin=False, is_global=True,
            read_only=False, allow_install=False, allow_uninstall=False,
            allow_reboot=False, allow_schedule=False, allow_wol=False,
            allow_snapshot_creation=False, allow_snapshot_removal=False,
            allow_snapshot_revert=False, allow_tag_creation=False,
            allow_tag_removal=False, deny_all=False,date_created=None,
            date_modified=None
            ):
        self.group_id = group_id
        self.is_admin = is_admin
        self.is_global = is_global
        self.read_only = read_only
        self.allow_install = allow_install
        self.allow_uninstall = allow_uninstall
        self.allow_reboot = allow_reboot
        self.allow_schedule = allow_schedule
        self.allow_wol = allow_wol
        self.allow_snapshot_creation = allow_snapshot_creation
        self.allow_snapshot_removal = allow_snapshot_removal
        self.allow_snapshot_revert = allow_snapshot_revert
        self.allow_tag_creation = allow_tag_creation
        self.allow_tag_removal = allow_tag_removal
        self.deny_all = deny_all
        self.date_created = date_created
        self.date_modified = date_modified
    def __repr__(self):
        return "<GlobalGroupAccess(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.group_id, self.is_admin, self.is_global,
                self.read_only, self.allow_install, self.allow_uninstall,
                self.allow_reboot, self.allow_schedule, self.allow_wol,
                self.allow_snapshot_creation, self.allow_snapshot_removal,
                self.allow_snapshot_revert, self.allow_tag_creation,
                self.allow_tag_removal, self.deny_all, self.date_created,
                self.date_modified
                )



class TagUserAccess(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "tag_user_access"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    tag_id = Column(INTEGER(unsigned=True),
            ForeignKey("tag_info.id"))
    read_only = Column(BOOLEAN, nullable=False)          # True = Up, False = Down
    allow_install = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_uninstall = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_reboot = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_schedule = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_wol = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_revert = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    date_created = Column(DATETIME, nullable=True)
    date_modified = Column(DATETIME, nullable=True)
    def __init__(self, tag_id, user_id, read_only=False, allow_install=False,
            allow_uninstall=False, allow_reboot=False, allow_schedule=False,
            allow_wol=False, allow_snapshot_creation=False,
            allow_snapshot_removal=False, allow_snapshot_revert=False,
            allow_tag_creation=False, allow_tag_removal=False,
            date_created=None, date_modified=None
            ):
        self.tag_id = tag_id
        self.user_id = user_id
        self.read_only = read_only
        self.allow_install = allow_install
        self.allow_uninstall = allow_uninstall
        self.allow_reboot = allow_reboot
        self.allow_schedule = allow_schedule
        self.allow_wol = allow_wol
        self.allow_snapshot_creation = allow_snapshot_creation
        self.allow_snapshot_removal = allow_snapshot_removal
        self.allow_snapshot_revert = allow_snapshot_revert
        self.allow_tag_creation = allow_tag_creation
        self.allow_tag_removal = allow_tag_removal
        self.date_created = date_created
        self.date_modified = date_modified
    def __repr__(self):
        return "<TagUserAccess(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.tag_id, self.user_id, self.read_only, self.allow_install,
                self.allow_uninstall, self.allow_reboot,
                self.allow_schedule, self.allow_wol,
                self.allow_snapshot_creation,
                self.allow_snapshot_removal,
                self.allow_snapshot_revert,
                self.allow_tag_creation, self.allow_tag_removal,
                self.date_created, self.date_modified
                )


class TagGroupAccess(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "tag_group_access"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    tag_id = Column(INTEGER(unsigned=True),
            ForeignKey("tag_info.id"))
    group_id = Column(INTEGER, ForeignKey('groups.id'))
    read_only = Column(BOOLEAN, nullable=False)          # True = Up, False = Down
    allow_install = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_uninstall = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_reboot = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_schedule = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_wol = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_revert = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    date_created = Column(DATETIME, nullable=True)
    date_modified = Column(DATETIME, nullable=True)
    def __init__(self, tag_id, group_id=None, read_only=False,
            allow_install=False, allow_uninstall=False,
            allow_reboot=False, allow_schedule=False,
            allow_wol=False, allow_snapshot_creation=False,
            allow_snapshot_removal=False, allow_snapshot_revert=False,
            allow_tag_creation=False, allow_tag_removal=False,
            date_created=None, date_modified=None
            ):
        self.tag_id = tag_id
        self.group_id = group_id
        self.read_only = read_only
        self.allow_install = allow_install
        self.allow_uninstall = allow_uninstall
        self.allow_reboot = allow_reboot
        self.allow_schedule = allow_schedule
        self.allow_wol = allow_wol
        self.allow_snapshot_creation = allow_snapshot_creation
        self.allow_snapshot_removal = allow_snapshot_removal
        self.allow_snapshot_revert = allow_snapshot_revert
        self.allow_tag_creation = allow_tag_creation
        self.allow_tag_removal = allow_tag_removal
        self.date_created = date_created
        self.date_modified = date_modified
    def __repr__(self):
        return "<TagGroupAccess(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.tag_id, self.group_id, self.read_only, self.allow_install,
                self.allow_uninstall, self.allow_reboot,
                self.allow_schedule, self.allow_wol,
                self.allow_snapshot_creation,
                self.allow_snapshot_removal,
                self.allow_snapshot_revert,
                self.allow_tag_creation, self.allow_tag_removal,
                self.date_created, self.date_modified
                )


class NodeUserAccess(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "node_user_access"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    node_id = Column(INTEGER(unsigned=True),
            ForeignKey("node_info.id"))
    read_only = Column(BOOLEAN, nullable=False)          # True = Up, False = Down
    allow_install = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_uninstall = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_reboot = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_schedule = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_wol = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_revert = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    date_created = Column(DATETIME, nullable=True)
    date_modified = Column(DATETIME, nullable=True)
    def __init__(self, node_id, user_id=None, read_only, allow_install=False,
            allow_uninstall=False, allow_reboot=False, allow_schedule=False,
            allow_wol=False, allow_snapshot_creation=False,
            allow_snapshot_removal=False, allow_snapshot_revert=False,
            allow_tag_creation=False, allow_tag_removal=False,
            date_created=None, date_modified=None
            ):
        self.node_id = node_id
        self.user_id = user_id
        self.read_only = read_only
        self.allow_install = allow_install
        self.allow_uninstall = allow_uninstall
        self.allow_reboot = allow_reboot
        self.allow_schedule = allow_schedule
        self.allow_wol = allow_wol
        self.allow_snapshot_creation = allow_snapshot_creation
        self.allow_snapshot_removal = allow_snapshot_removal
        self.allow_snapshot_revert = allow_snapshot_revert
        self.allow_tag_creation = allow_tag_creation
        self.allow_tag_removal = allow_tag_removal
        self.date_created = date_created
        self.date_modified = date_modified
    def __repr__(self):
        return "<NodeUserAccess(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.node_id, self.user_id, self.read_only, self.allow_install,
                self.allow_uninstall, self.allow_reboot,
                self.allow_schedule, self.allow_wol,
                self.allow_snapshot_creation,
                self.allow_snapshot_removal,
                self.allow_snapshot_revert,
                self.allow_tag_creation, self.allow_tag_removal,
                self.date_created, self.date_modified
                )



class NodeGroupAccess(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "node_group_access"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    node_id = Column(INTEGER(unsigned=True),
            ForeignKey("node_info.id"))
    group_id = Column(INTEGER, ForeignKey('groups.id'))
    read_only = Column(BOOLEAN, nullable=False)          # True = Up, False = Down
    allow_install = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_uninstall = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_reboot = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_schedule = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_wol = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_snapshot_revert = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_creation = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    allow_tag_removal = Column(BOOLEAN, nullable=False)   # True = Up, False = Down
    date_created = Column(DATETIME, nullable=True)
    date_modified = Column(DATETIME, nullable=True)
    def __init__(self, node_id, group_id=None, read_only=False,
            allow_install=False, allow_uninstall=False,
            allow_reboot=False, allow_schedule=False,
            allow_wol=False, allow_snapshot_creation=False,
            allow_snapshot_removal=False, allow_snapshot_revert=False,
            allow_tag_creation=False, allow_tag_removal=False,
            date_created=None, date_modified=None
            ):
        self.node_id = node_id
        self.group_id = group_id
        self.read_only = read_only
        self.allow_install = allow_install
        self.allow_uninstall = allow_uninstall
        self.allow_reboot = allow_reboot
        self.allow_schedule = allow_schedule
        self.allow_wol = allow_wol
        self.allow_snapshot_creation = allow_snapshot_creation
        self.allow_snapshot_removal = allow_snapshot_removal
        self.allow_snapshot_revert = allow_snapshot_revert
        self.allow_tag_creation = allow_tag_creation
        self.allow_tag_removal = allow_tag_removal
        self.date_created = date_created
        self.date_modified = date_modified
    def __repr__(self):
        return "<NodeGroupAccess(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)>" %\
                (
                self.node_id, self.group_id, self.read_only,
                self.allow_install, self.allow_uninstall,
                self.allow_reboot, self.allow_schedule,
                self.allow_wol, self.allow_snapshot_creation,
                self.allow_snapshot_removal,
                self.allow_snapshot_revert,
                self.allow_tag_creation, self.allow_tag_removal,
                self.date_created, self.date_modified
                )

