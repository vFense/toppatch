"""
Simple script to create the tables of the database from the model sources.
"""

import sys
sys.path.append("/opt/TopPatch/tp/src")

from sqlalchemy import create_engine

from models.base import Base
from models.account import *
from models.oauth.token import *
from models.application import *
from models.scanner import *
from models.cve import *


engine = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls', echo=False)



Base.metadata.create_all(engine)
