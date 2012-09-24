#!/usr/bin/env python                                                                                                                            


from datetime import datetime
from socket import getfqdn
from models.base import Base
from models.windows import *
from models.node import *

def nodeExists(session, node):
    node = \
        session.query(NodeInfo).filter_by(ip_address=node).first()
    return(node)

def operationExists(session, oper_id):
    oper = \
        session.query(Operations).filter_by(operation_id=oper_id)
    exists = oper.first()
    return(exists, oper)
