
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
    """ 
        Return a json object containing the nodes and the related packages
        concerning that node within the tag name.
        arguments below..
        session == sqlalchemy session object
        tpid == the toppatch_id of the package
        tagid == The id of the tag name
        or
        tagname == the tagname of the tag
    """
    session = validate_session
    tag_id = None
    if tagid;
        tag_id = tagid
    elif tagname:
        tag_exists = session.query(TagInfo).filter(TagInfo.tag == tagname.first()
        if tag_exists:
            tag_id = tag_exists.id
    list_of_nodes = session.query(PackagesPerNode).\
            filter(PackagePerNode.toppatch_id == tpid).all()
    if len(list_of_nodes) >0:
        for node in list_of_nodes:
            list_of_tags = session.query(TagsPerNode).\
                    filter(TagsPerNode.node_id == node.node_id).all()
            if len (list_of_tags) >0:
                
            
