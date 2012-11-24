
from time import sleep
from db.query_tables import *
from db.update_tables import *
from db.client import validateSession


def retrieveDependencies(session, msg):
    session = validateSession
    AgentOperation(
    dep_exists = session.query(LinuxPackageDependency).filter(LinuxPackageDependency.toppatch_id == pkg_id).first()
