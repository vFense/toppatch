#!/usr/bin/env python                                                                                                                            


from datetime import datetime
from socket import getfqdn
from models.base import Base
from models.windows import *
from models.node import *
from models.ssl import *

def nodeExists(session, node=None, node_id=None):
    if not node_id:
        node = \
            session.query(NodeInfo).filter_by(ip_address=node).first()
    else:
        node = \
            session.query(NodeInfo).filter_by(id=node_id).first()
    return(node)

def operationExists(session, oper_id):
    oper = \
        session.query(Operations).filter_by(id=oper_id)
    exists = oper.first()
    return(exists, oper)

def csrExists(session, node=None):
    node = \
        session.query(CsrInfo).filter_by(ip_address=node).first()
    return(node)
    
