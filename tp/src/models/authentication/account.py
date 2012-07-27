
from models.base import Base

from sqlalchemy import String, Column, Integer

class User(Base):
    """ Basic User Account class representing a record from the 'accounts' table.

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

class Developer(Base):
    """ Class that helps and defines a row in the "developers" table. """
    __tablename__ = "developers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    client_id = Column(String(255))
    client_secret = Column(String(255))
    redirect_uri = Column(String(255))

    def __init__(self, name, client_id, client_secret, redirect=None):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect