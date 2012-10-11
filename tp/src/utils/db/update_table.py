#!/usr/bin/env python


from datetime import datetime
from socket import gethostbyaddr
from models.base import Base
from models.windows import *
from models.node import *
from utils.common import *
from utils.db.query_table import *


#WebsocketHandler.sendMessage(message)
def addNode(session, client_ip, agent_timestamp=None, node_timestamp=None):
    try:
        hostname = gethostbyaddr(client_ip)[0]
    except:
        hostname = None
    try:
        add_node = NodeInfo(client_ip, hostname,
                True, True, datetime.now(), datetime.now())
        session.add(add_node)
        session.commit()
        return add_node
    except Exception as e:
        print e

def addCsr(session, client_ip, location, csr_name,
            signed=False, signed_date=False):
    try:
        add_csr = CsrInfo(csr_name, client_ip, location, signed, signed_date)
        session.add(add_csr)
        session.commit()
        return add_csr
    except Exception as e:
        print e

def addCert(session, node_id, cert_id, cert_name,
            cert_location, cert_expiration):
    try:
        add_cert = SslInfo(node_id, cert_id, cert_name,
                    cert_location, cert_expiration)
        session.add(add_cert)
        session.commit()
        print add_cert
        return add_cert
    except Exception as e:
        print e

def addOperation(session, node_id, operation, result_id=None,
        operation_sent=None, operation_received=None, results_received=None):
    add_oper = Operations(node_id, operation, result_id,
            operation_sent, operation_received, results_received
            )
    if add_oper:
        session.add(add_oper)
        session.commit()
        return add_oper
        #WebsocketHandler.sendMessage("ITS ME")


def addSystemInfo(session, data, node_info):
    exists, operation = operationExists(session, data['operation_id'])
    if exists:
        operation.update({'results_received' : datetime.now()})
        system_info = SystemInfo(node_info.id, data['os_code'],
            data['os_string'], data['version_major'],
            data['version_minor'], data['version_build'],
            data['meta'], 
            )
        if system_info:
            session.add(system_info)
            session.commit()
            return system_info


def addWindowsUpdate(session, data):
    exists, operation = operationExists(session, data['operation_id'])
    if exists:
        operation.update({'results_received' : datetime.now()})
        session.commit()
        for update in data['data']:
            update_exists = updateExists(session, update['toppatch_id'])
            if not update_exists:
                win_update = WindowsUpdate(update['toppatch_id'],
                        update['kb'], update['vendor_id'],update['title'],
                        update['description'], update['support_url'],
                        update['severity'], dateParser(update['date_published']),
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
    if exists:
        node_id = exists.node_id
        operation.update({'results_received' : datetime.now()})
        session.commit()
        for addupdate in data['data']:
            update_exists, foo = nodeUpdateExists(session, node_id, addupdate['toppatch_id'])
            if not update_exists:
                if 'date_installed' in addupdate:
                    date_installed = dateParser(addupdate['date_installed'])
                else:
                    date_installed = None
                hidden = returnBool(addupdate['hidden'])
                installed = returnBool(addupdate['installed'])
                node_update = ManagedWindowsUpdate(node_id,
                        addupdate['toppatch_id'],
                        date_installed, hidden, installed=installed
                        )
                try:
                    session.add(node_update)
                    session.commit()
                    #WebsocketHandler.sendMessage("ITS ME")
                except:
                    session.rollback()
                #finally:
                #    addWindowsUpdate(session, data)

def addSoftwareAvailable(session, data):
    exists, operation = operationExists(session, data['operation_id'])
    if exists:
        node_id = exists.node_id
        operation.update({'results_received' : datetime.now()})
        session.commit()
        for software in data['data']:
            software_exists = softwareExists(session, software['name'], \
                    software['version'])
            if not software_exists:
                software_update = SoftwareAvailable(node_id,\
                            software['name'], software['vendor'], \
                            software['version']
                            )
                try:
                    session.add(software_update)
                    session.commit()
                except:
                    session.rollback()

def addSoftwareInstalled(session, data):
    exists, operation = operationExists(session, data['operation_id'])
    if exists:
        node_id = exists.node_id
        operation.update({'results_received' : datetime.now()})
        session.commit()
        for software in data['data']:
            software_exists = softwareExists(session, software['name'], \
                    software['version'])
            if software_exists:
                node_software_exists = nodeSoftwareExists(session, \
                    software_exists.id)
                if not node_software_exists:
                    #if 'date_installed' in data:
                    #    date_installed = dateParser(software['date_installed'])
                    #else:
                    #    date_installed = None
                    software_update = SoftwareInstalled(node_id,
                            software_exists.id
                            #date_installed
                            )
                    try:
                        session.add(software_update)
                        session.commit()
                    except:
                        session.rollback()

def updateOperationRow(session, oper_id, results_recv=None, oper_recv=None):
    exists, operation = operationExists(session, oper_id)
    if exists and results_recv:
        operation.update({'results_received' : datetime.now()})
        session.commit()
    elif exists and oper_recv:
        operation.update({'operation_received' : datetime.now()})
        session.commit()

def updateNode(session, node_id):
    exists, node = nodeExists(session, node_id=node_id)
    if exists:
        exists.update({'last_agent_update' : datetime.now(),
                'last_node_update' : datetime.now()})
        session.commit()
        return node

def addResults(session, data):
    exists, operation = operationExists(session, data['operation_id'])
    if exists:
        node_id = exists.node_id
        for msg in data['data']:
            update_exists, update_oper = nodeUpdateExists(session, node_id, msg['toppatch_id'])
            if update_exists:
                update_oper.update({'installed' : True, 'date_installed' : datetime.now()})
            reboot = returnBool(msg['reboot'])
            error = None
            if "error" in msg:
                error = msg['error']
            results = Results(node_id, data['operation_id'], \
                        msg['toppatch_id'], msg['result'], \
                        reboot, error
                        )
            try:
                session.add(results)
                session.commit()
                operation.update({'results_id' : results.id})
                ui = len(session.query(ManagedWindowsUpdate).filter_by(node_id=node_id).filter_by(installed=True).all())
                un = len(session.query(ManagedWindowsUpdate).filter_by(node_id=node_id).filter_by(installed=False).all())
                ns_oper = session.query(NodeStats).filter_by(node_ID=node_id)
                ns_oper.update({"patches_installed" : ui, "patches_available" : un})
                nui = len(session.query(ManagedWindowsUpdate).filter_by(installed=True).all())
                nun = len(session.query(ManagedWindowsUpdate).filter_by(installed=False).all())
                nns_oper = session.query(NetworkStats).filter_by(id=1)
                nns_oper.update({"patches_installed" : nui, "patches_available" : nun})
                session.commit()
                return results
                #WebsocketHandler.sendMessage("ITS ME")
            except:
                session.rollback()
