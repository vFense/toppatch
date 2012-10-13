#!/usr/bin/env python


from datetime import datetime
from socket import gethostbyaddr
from models.base import Base
from models.windows import *
from models.node import *
from utils.common import *
from utils.db.query_table import *
from utils.tcpasync import TcpConnect


#WebsocketHandler.sendMessage(message)
def addNode(session, client_ip, agent_timestamp=None, node_timestamp=None):
    try:
        hostname = gethostbyaddr(client_ip)[0]
    except:
        hostname = None
    try:
        add_node = NodeInfo(client_ip, hostname,
                True, True, agent_timestamp, node_timestamp)
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
        installed_oper = session.query(ManagedWindowsUpdate).filter_by(installed=True).filter_by(node_id=node_id)
        installed = installed_oper.first()
        pending_oper = session.query(ManagedWindowsUpdate).filter_by(pending=True).filter_by(node_id=node_id)
        pending = pending_oper.first()
        if installed and pending:
            pending_oper.update({"pending" : False})
            session.commit()
        return node

def updateNodeNetworkStats(session, node_id):
    nodeupdates = session.query(ManagedWindowsUpdate).filter_by(node_id=node_id)
    patchesinstalled = nodeupdates.filter_by(installed=True).all()
    patchesuninstalled = nodeupdates.filter_by(installed=False).all()
    patchespending = nodeupdates.filter_by(pending=True).all()
    nodestats = session.query(NodeStats).filter_by(node_id=node_id)
    nodeexists = nodestats.first()
    if nodeexists:
        nodestats.update({"patches_installed" : len(patchesinstalled),
                          "patches_available" : len(patchesuninstalled),
                          "patches_pending" : len(patchespending)})
    else:
        add_node_stats = NodeStats(node_id, len(patchesinstalled), \
                          len(patchesuninstalled), len(patchespending), 0)
        session.add(add_node_stats)
    nstats = session.query(ManagedWindowsUpdate)
    totalinstalled = nstats.filter_by(installed=True).all()
    totalnotinstalled = nstats.filter_by(installed=False).all()
    totalpending = nstats.filter_by(pending=True).all()
    networkstats = session.query(NetworkStats)
    networkstatsexists = networkstats.filter_by(id=1).first()
    if networkstatsexists:
        networkstats.update({"patches_installed" : len(totalinstalled),
                             "patches_available" : len(totalnotinstalled),
                             "patches_pending" : len(totalpending)})
    else:
        network_sstats_init = NetworkStats(len(totalinstalled),
                              len(totalnotinstalled), len(totalpending), 0)
        session.add(network_sstats_init)

    session.commit()

def updateRebootStatus(session, data):
    node, node_exists = nodeExists(session,node_id=data['node_id'])
    print node
    if exists:
        node_id = exists.node_id
        if data['operation'] == 'reboot':
            node.update({'reboot' : False})
            session.commit()

def addResults(session, data):
    exists, operation = operationExists(session, data['operation_id'])
    node, node_exists = nodeExists(session,node_id=data['node_id'])
    print node
    if exists:
        node_id = exists.node_id
        if data['operation'] == 'reboot':
            node.update({'reboot' : False})
            session.commit()
        for msg in data['data']:
            print msg
            if 'reboot' in msg:
                reboot = returnBool(msg['reboot'])
            else:
               reboot = None
            update_exists, update_oper = nodeUpdateExists(session, node_id, msg['toppatch_id'])
            if update_exists:
                if data['operation'] == "install" and msg['result'] == 'success':
                    print "patch installed on %s %s" % ( node_id, msg['toppatch_id'] )
                    update_oper.update({'installed' : True, 
                                        'date_installed' : datetime.now(),
                                        'pending' : False})
                    if reboot:
                        if node_exists.reboot == False:
                            node.update({'reboot' : reboot})
                elif data['operation'] == "install" and msg['result'] == 'failed':
                    update_oper.update({'installed' : False,
                                        'date_installed' : datetime.now(),
                                        'pending' : False})
                    if reboot:
                        if node_exists.reboot == False:
                            node.update({'reboot' : reboot})
                elif data['operation'] == "uninstall" and msg['result'] == 'success':
                    print "deleting patch from managed_windows_updates %s on node_id %s" % ( msg['toppatch_id'], node_id )
                    update_oper.update({'installed' : False,
                                        'pending' : False})
                    if reboot:
                        if node_exists.reboot == False:
                            node.update({'reboot' : reboot})
                elif data['operation'] == "uninstall" and msg['result'] == 'failed':
                    update_oper.update({'installed' : True, 'date_installed' : datetime.now()})
                    if reboot:
                        if node_exists.reboot == False:
                            node.update({'reboot' : reboot})
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
                operation.update({'results_id' : results.id,
                                  'results_received' : datetime.now()})
                updateNodeNetworkStats(session, node_id)
                TcpConnect("127.0.0.1", "FUCK YOU", port=8080, secure=False)
                return results
            except:
                session.rollback()
