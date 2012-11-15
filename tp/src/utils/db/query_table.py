#!/usr/bin/env python                                                                                                                            


from datetime import datetime
from socket import getfqdn
from models.base import Base
from models.windows import *
from models.node import *
from models.scheduler import *
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

def timeBlockExists(session, id=None, label=None, start_date=None, start_time=None):
    if id:
        tb_object = \
            session.query(TimeBlocker).filter_by(id=id)
    elif label and start_date and start_time:
        print label, start_date, start_time
        tb_object = \
            session.query(TimeBlocker).filter_by(name=label).filter_by(start_date=start_date).filter_by(start_time=start_time)
    tb = tb_object.first()
    return(tb_object, tb)

def operationExistsUsingNodeId(session, node_id, oper_type):
    oper = \
        session.query(Operations).filter_by(node_id=node_id).filter_by(results_received=None).filter_by(operation_type=oper_type)
    exists = oper.first()
    return(exists, oper)

def csrExists(session, node):
    csr = \
        session.query(CsrInfo).filter_by(ip_address=node)
    exists = csr.first()
    return(exists, csr)

def certExists(session, node):
    cert = \
        session.query(SslInfo).filter_by(node_id=node)
    exists = cert.first()
    return(exists, cert)

def updateExists(session, tp_id):
    update = \
        session.query(WindowsUpdate).filter_by(toppatch_id=tp_id).first()
    return(update)

def nodeUpdateExists(session, node, tp_id):
    update = \
        session.query(ManagedWindowsUpdate).filter_by(node_id=node).filter_by(toppatch_id=tp_id)
    exists = update.first()
    return(exists, update)

def softwareExists(session, sname, sversion):
    software = \
        session.query(SoftwareAvailable).filter_by(name=sname).filter_by(version=sversion).first()
    return(software)

def nodeSoftwareExists(session, sid):
    software = \
        session.query(SoftwareInstalled).filter_by(id=sid).first()
    return(software)
