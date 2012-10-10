from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def initEngine():
    db = create_engine(
            'mysql://root:topmiamipatch@127.0.0.1/toppatch_server', 
            pool_size=0, pool_recycle=60
            )
    return db

def createSession(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
