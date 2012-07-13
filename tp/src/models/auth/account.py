
from models.base import Base

from sqlalchemy import String, Column, Integer, Text

class Account(Base):
    """ Basic Account class representing a record from the 'accounts' table.

    An account represents a user of the TP program. Consist of a name, email, and password.

    """
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))

    def __init__(self, name, password, email=None):
        self.name = name
        self.password = password
        self.email = email
