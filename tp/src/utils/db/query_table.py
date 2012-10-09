#!/usr/bin/env python                                                                                                                            


from datetime import datetime
from socket import getfqdn
from models.base import Base
from models.windows import *
from models.node import *
from models.ssl import *

def nodeExists(session, node_ip=None, node_id=None):
    node = None
    if not node_id:
        node = \
            session.query(NodeInfo).filter_by(ip_address=node_ip)
    else:
        node = \
            session.query(NodeInfo).filter_by(id=node_id)
    exists = node.first()
    return(node, exists)

def operationExists(session, oper_id):
    oper = \
        session.query(Operations).filter_by(id=oper_id)
    exists = oper.first()
    return(exists, oper)

def csrExists(session, node):
    csr = \
        session.query(CsrInfo).filter_by(ip_address=node).first()
    return(csr)
    

def nodeUpdateExists(session, node, tp_id):
    update = \
        session.query(ManagedWindowsUpdate).filter_by(node_id=node).filter_by(toppatch_id=tp_id).first()
    return(update)

def softwareExists(session, sname, sversion):
    software = \
        session.query(SoftwareAvailable).filter_by(name=sname).filter_by(version=sversion).first()
    return(software)

def nodeSoftwareExists(session, sid):
    software = \
        session.query(SoftwareInstalled).filter_by(id=sid).first()
    return(software)
