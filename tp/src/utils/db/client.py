import logging
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from apscheduler.scheduler import Scheduler
from models.node import NodeInfo


def initEngine():
    db = create_engine(
            'mysql://root:topmiamipatch@127.0.0.1/toppatch_server', 
            pool_size=0, pool_recycle=3600, pool_reset_on_return='rollback'
            )
    return db

def createSession(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
"""
def validateSession(session):
    def returnSession(fn):
        try:
            fn()
            print "BAM I WORKED"
        except Exception as e:
            session.rollback()
            print "I had to rollback"
            fn()
    return returnSession
"""
def validateSession(session):
    try:
        session.query(NodeInfo).first()
    except Exception as e:
        if e.connection_invalidated:
            session.rollback()
    return session

#ENGINE = initEngine()
#session = createSession(ENGINE)

#@validateSession(session)
#def foo():
#    print session.query(NodeInfo).first()
