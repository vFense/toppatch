from models.windows import *
from models.node import *
from models.base import Base
from sqlalchemy import String, Column, Integer, Text, ForeignKey, schema, types, create_engine

db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
db.echo = True
Base.metadata.create_all(db)
