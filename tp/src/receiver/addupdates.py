#!/usr/bin/env python


from datetime import datetime
from socket import gethostbyaddr
from models.base import Base                                                                                                                     
from models.windows import *
from models.node import *

from dbquery import *

def addNode(session, client_ip):
    try:
        hostname = gethostbyaddr(client_ip)[0]
    except:
        hostname = None
    try:
        add_node = NodeInfo(client_ip, hostname,
                True, True, datetime.now(), datetime.now())
        session.add(add_node)
        session.commit()
    except Exception as e:
        print e


def addSystemInfo(session, data, operation):
    exists, operation = operationsExists(session, data['operation_id'])
    if exists:
        operation.update({'operation_received' : datetime.now()})
    system_info = SystemInfo(node_info.id, data['os_code'],
        data['os_string'], data['os_version_major'],
        data['os_version_minor'], data['os_version_build'],
        data['os_meta']
        )
    if system_info:
        session.add(system_info)
        session.commit()

#def addOperationReceived(session, data):

#def updateOperationReceived(session, data, operation);

#def addWindowsUpdate(session, data):

#def addManagedWindowsUpdate(session, data):

#def addResults(session, data):
