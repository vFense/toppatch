
from models.base import Base

from sqlalchemy import String, Column, Integer, Text

class Account(Base):
    """ Basic Account class representing a record from the 'accounts' table.

    An account represents a user of the TP program. Consist of a name, email, and password.

    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    hash = Column(String(255))
    fullname = Column(String(255))
    email = Column(String(255))

    def __init__(self, username, password, fullname=None, email=None):
        self.username = username
        self.hash = password
        self.fullname = fullname
        self.email = email
