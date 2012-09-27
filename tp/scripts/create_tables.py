#!/usr/bin/env python
from models.base import Base
from models.windows import *
from models.node import *
from sqlalchemy import create_engine

db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
db.echo = True
db.drop(NodeInfo)
db.drop(SystemInfo)
db.drop(Operations)
db.drop(Results)
db.drop(SoftwareInstalled)
db.drop(WindowsUpdate)
db.drop(ManagedWindowsUpdate)
db.drop(CsrInfo)
db.drop(SslInfo)
Base.metadata.drop_all(db)
db.create(NodeInfo)
db.create(Operations)
db.create(Results)
db.create(SoftwareInstalled)
db.create(WindowsUpdate)
db.create(ManagedWindowsUpdate)
db.create(CsrInfo)
db.create(SslInfo)
Base.metadata.create_all(db)
