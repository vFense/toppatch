import logging
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
from apscheduler.scheduler import Scheduler
from models.node import NodeInfo


def init_engine():
    db = create_engine(
            'mysql://root:topmiamipatch@127.0.0.1/toppatch_server',
            pool_size=0, pool_recycle=3600, pool_reset_on_return='rollback'
            )
    return db


def create_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def validate_session(session):
    try:
        session.query(NodeInfo).first()
    except Exception as e:
        if e.connection_invalidated:
            session.rollback()
    return session


