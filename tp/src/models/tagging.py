#!/usr/bin/env python
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine
from sqlalchemy.dialects.mysql import INTEGER, BOOLEAN, CHAR, DATETIME, TIME, TEXT, TINYINT, VARCHAR
from sqlalchemy.orm import relationship, backref


class TagInfo(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "tag_info"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    tag = Column(VARCHAR(64), nullable=False, unique=True)
    date_created = Column(DATETIME, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    def __init__(self, tag, date_created, user_id):
        self.tag = tag
        self.date_created = date_created
        user_id = user_id
    def __repr__(self):
        return "<TagInfo(%s,%s,%s)>" %\
                (
                self.tag, self.date_created, self.user_id
                )

class TagsPerNode(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "tags_per_node"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    tag_id = Column(INTEGER(unsigned=True),
            ForeignKey("tag_info.id"))
    node_id = Column(INTEGER(unsigned=True),
            ForeignKey("node_info.id"))
    node_added_to_label = Column(DATETIME, nullable=True)
    def __init__(self, tag_id, node_id, node_added_to_label):
        self.tag_id = tag_id
        self.node_id = node_id
        self.node_added_to_label = node_added_to_label
    def __repr__(self):
        return "<TagsPerNode(%s,%s,%s)>" %\
                (
                self.tag_id, self.node_id, self.node_added_to_label
                )

class TagsPerUser(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "tags_per_user"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    tag_id = Column(INTEGER(unsigned=True),
            ForeignKey("tag_info.id"))
    #user_id = Column(INTEGER(unsigned=True),
    #        ForeignKey("users.id"))
    user_id = Column(Integer, ForeignKey('users.id'))
    user_added_to_label = Column(DATETIME, nullable=True)
    def __init__(self, tag_id, user_id, user_added_to_label):
        self.tag_id = tag_id
        self.user_id = user_id
        self.user_added_to_label = user_added_to_label
    def __repr__(self):
        return "<TagsPerUser(%s,%s,%s)>" %\
                (
                self.tag_id, self.user_id, self.user_added_to_label
                )


class TagStats(Base):
    """
    Represents one row from the hosts table.
    """
    __tablename__ = "tag_stats"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(INTEGER(unsigned=True),primary_key=True, autoincrement=True)
    tag_id = Column(INTEGER(unsigned=True),ForeignKey("tag_info.id"))
    patches_installed = Column(INTEGER(unsigned=True))
    patches_available = Column(INTEGER(unsigned=True))
    patches_pending = Column(INTEGER(unsigned=True))
    patches_failed = Column(INTEGER(unsigned=True))
    def __init__(self, tag_id, patches_installed,
                patches_available, patches_pending,
                patches_failed
                ):
        self.tag_id = tag_id
        self.patches_installed = patches_installed
        self.patches_available = patches_available
        self.patches_pending = patches_pending
        self.patches_failed = patches_failed
    def __repr__(self):
        return "<TagStats(%d,%d,%d,%d,%d)>" %\
                (
                self.tag_id, self.patches_installed,
                self.patches_available, self.patches_pending,
                self.patches_failed
                )

