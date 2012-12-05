import logging
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, scoped_session
from apscheduler.scheduler import Scheduler
from models.node import NodeInfo


def init_engine():
    """
        initialize the SQLAlchemy Engine to communicate with 
        the RV database.
    """
    db = create_engine(
            'mysql://root:topmiamipatch@127.0.0.1/toppatch_server',
            pool_size=0, pool_recycle=3600, pool_reset_on_return='rollback'
            )
    return db


def create_session(engine):
    """
        initialize a SQLAlchemy session to execute sql orm statements with 
        the RV database.
    """
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()
    return session


def validate_session(session):
    """
        This function should be the 1st call before any session call in 
        any of the RV methods, Classes, or functions.
    """
    try:
        session.query(NodeInfo).first()
    except Exception as e:
        print e
        if e.connection_invalidated:
            session.rollback()
    return session


