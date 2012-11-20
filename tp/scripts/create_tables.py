#!/usr/bin/env python
from models.base import Base
from models.account import *
from models.oauth.token import *
from models.application import *
from models.scanner import *
from models.cve import *
from models.packages import *
from models.node import *
from models.ssl import *
from models.scheduler import *
from models.tagging import *
from sqlalchemy import create_engine

db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
db.echo = True
#db.drop(TimeBlocker)
#Base.metadata.drop_all(db)
Base.metadata.create_all(db)
