#!/usr/bin/env python
from models.base import Base
from models.account import *
#from models.oauth.token import *
#from models.application import *
#from models.scanner import *
#from models.cve import *
#from models.windows import *
from models.node import *
#from models.ssl import *
from models.scheduler import *
from models.tagging import *
from sqlalchemy import create_engine

db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
db.echo = True
"""
db.drop(NodeInfo)
db.drop(SystemInfo)
db.drop(Operations)
db.drop(Results)
db.drop(SoftwareAvailable)
db.drop(SoftwareInstalled)
db.drop(WindowsUpdate)
db.drop(ManagedWindowsUpdate)
db.drop(CsrInfo)
db.drop(SslInfo)
"""
#db.drop(TimeBlocker)
Base.metadata.drop_all(db)


"""
db.create(NodeInfo)
db.create(Operations)
db.create(Results)
db.create(SoftwareAvailable)
db.create(SoftwareInstalled)
db.create(WindowsUpdate)
db.create(ManagedWindowsUpdate)
db.create(CsrInfo)
db.create(SslInfo)
"""
Base.metadata.create_all(db)
