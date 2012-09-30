from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def connect():
    db = create_engine(
            'mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
    Session = sessionmaker(bind=db)
    session = Session()
    return session
