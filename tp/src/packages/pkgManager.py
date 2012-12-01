
from time import sleep
from db.query_tables import *
from db.update_tables import *
from db.client import validate_session


def retrieveDependencies(session, msg):
    session = validate_session
    AgentOperation()
    dep_exists = session.query(LinuxPackageDependency).
            filter(LinuxPackageDependency.toppatch_id == pkg_id).first()


def list_packages_by_tag(session, tpid, tagid=None, tagname=None):
    tag_id = None
    if tagid;
        tag_id = tagid
    elif tagname:
        tag_exists = session.query(TagInfo)
