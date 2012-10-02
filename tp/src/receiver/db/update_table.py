#!/usr/bin/env python


from datetime import datetime
from socket import gethostbyaddr
from models.base import Base                                                                                                                     
from models.windows import *
from models.node import *

from query_table import *

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

def addCsr(session, client_ip, location):
    csr_name = client_ip + '.csr'
    csr_location = location + '/' + csr_name
    try:
        add_csr = CsrInfo(csr_name, client_ip, csr_location, None, None)
        session.add(add_csr)
        session.commit()
    except Exception as e:
        print e


def addOperation(session, node_id, operation, result_id=None,
        operation_sent=None, operation_received=None):
    add_oper = Operations(node_id, operation, result_id,
            operation_sent, operation_received
            )
    if add_oper:
        session.add(add_oper)
        session.commit()


def addSystemInfo(session, data, node_info):
    exists, operation = operationExists(session, data['operation_id'])
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


def addWindowsUpdate(session, data):
    exists, operation = operationExists(session, data['operation_id'])
    if exists:
        operation.update({'operation_received' : datetime.now()})
        for update in data['updates']:
            win_update = WindowsUpdate(update['toppatch_id'],
                    update['kb'], update['vendor_id'],update['title'],
                    update['description'], update['support_url'],
                    update['severity'], update['date_published'],
                    update['file_size']
                    )
            if win_update:
                try:
                    session.add(win_update)
                    session.commit()
                except:
                    session.rollback()

def addWindowsUpdatePerNode(session, data):
    exists, operation = operationExists(session, data['operation_id'])
    node_id = exists.node_id
    if exists:
        operation.update({'operation_received' : datetime.now()})
        for addupdate in data['updates']:
            if addupdate['date_installed'] == '':
               date_installed = None
            if addupdate['hidden']  == "true":
                hidden = True
            else:
                hidden = False
            node_update = ManagedWindowsUpdate(node_id,
                    addupdate['toppatch_id'],
                    date_installed, hidden
                    )
            if node_update:
                try:
                    session.add(node_update)
                    session.commit()
                except:
                    session.rollback()
                finally:
                    addWindowsUpdate(session, data)

#def addOperationReceived(session, data):

#def updateOperationReceived(session, data, operation);


#def addManagedWindowsUpdate(session, data):

#def addResults(session, data):
