"""
Simple script to create the tables of the database from the model sources.
"""
from sqlalchemy import create_engine

from models.base import Base
from models.authentication.account import *
from models.authentication.token import *
from models.application import *
from models.scanner import *
from models.cve import *



engine = create_engine('mysql://root:topmiamipatch@127.0.0.1/test_vuls', echo=True)



Base.metadata.create_all(engine)
