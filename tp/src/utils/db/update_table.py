#!/usr/bin/env python


from datetime import datetime
from socket import gethostbyaddr
from models.base import Base
from models.packages import *
from models.node import *
from models.tagging import *
from models.scheduler import *
from utils.common import *
from utils.db.client import *
from utils.db.query_table import *
from utils.tcpasync import TcpConnect


#WebsocketHandler.sendMessage(message)
def addNode(session, client_ip, agent_timestamp=None, node_timestamp=None):
    session = validateSession(session)
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

def addTag(session, tag_name, user_id=None):
    session = validateSession(session)
    date_created=datetime.now()
    try:
        add_tag = TagInfo(tag_name, date_created, user_id)
        session.add(add_tag)
        session.commit()
        return(True, "Tag %s added" % (tag_name), add_tag)
    except Exception as e:
        session.rollback()
        print e
        return(False, "Tag %s failed to add" % (tag_name))

def addDependency(session, data):
    session = validateSession(session)
    failed_count = 0
    for deps in data['data']:
        pkg_id = deps['toppatch_id']
        for dep in deps['dependencies']:
            dep_exists = session.query(LinuxPackageDependency).filter(LinuxPackageDependency.toppatch_id == pkg_id).filter(LinuxPackageDependency.dependency == dep).first()
            if not dep_exists:
                try:
                    dep_add = LinuxPackageDependency(pkg_id, dep)
                    session.add(dep_add)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    failed_count += 1

def addTagPerNode(session, nodes=[], tag_id=None, tag_name=None,
                user_id=None):
    session = validateSession(session)
    completed = False
    count = 0
    if not tag_id and tag_name:
        tag_object, tag = tagExists(session, tag_name=tag_name)
    elif tag_id and not tag_name:
        tag_object, tag = tagExists(session, tag_id=tag_id)
    if not tag and user_id:
        tag_added, tag_msg, tag = \
                addTag(session, tag_name, user_id=user_id)
    for node in nodes:
        tag_for_node_exists = \
            session.query(TagsPerNode).filter_by(node_id=node).filter_by(tag_id=tag.id).first()
        if not tag_for_node_exists:
            try:
                tag_added = TagsPerNode(tag.id, node, datetime.now())
                session.add(tag_added)
                session.commit()
            except Exception as e:
                session.rollback()
                count = count + 1
        else:
            count = count + 1
    if count >=1:
        return(False, "failed to add nodes to tag %s", tag.tag)
    else:
        return(True, "Nodes %s were added to tag %s" % (nodes, tag.tag), tag.tag)

def addTimeBlock(session, label, start_date, start_time, end_time,
                  days, end_date=None, span_end_date_time=None, span=False,
                  enabled=False):
    session = validateSession(session)
    try:
        add_block = TimeBlocker(label, start_date, start_time,
                                end_time, days, end_date,
                                span_end_date_time, span,
                                enabled)
        session.add(add_block)
        session.commit()
        return(True, "Time Block Added", add_block)
    except Exception as e:
        print e
        session.rollback()
        return(False, "Time Block Could Not Be Added", e)

def addCsr(session, client_ip, location, csr_name,
            signed=False, signed_date=False):
    session = validateSession(session)
    try:
        add_csr = CsrInfo(csr_name, client_ip, location, signed, signed_date)
        session.add(add_csr)
        session.commit()
        return add_csr
    except Exception as e:
        session.rollback()
        print e

def addCert(session, node_id, cert_id, cert_name,
            cert_location, cert_expiration):
    session = validateSession(session)
    try:
        add_cert = SslInfo(node_id, cert_id, cert_name,
                    cert_location, cert_expiration)
        session.add(add_cert)
        session.commit()
        print add_cert
        return add_cert
    except Exception as e:
        session.rollback()
        print e

def addOperation(session, node_id, operation, result_id=None,
        operation_sent=None, operation_received=None, results_received=None):
    add_oper = Operations(node_id, operation, result_id,
            operation_sent, operation_received, results_received
            )
    session = validateSession(session)
    if add_oper:
        session.add(add_oper)
        session.commit()
        return add_oper


def addSystemInfo(session, data, node_info):
    session = validateSession(session)
    exists, operation = operationExists(session, data['operation_id'])
    if exists:
        operation.update({'results_received' : datetime.now()})
        session.commit()
        system_info = SystemInfo(node_info.id, data['os_code'],
            data['os_string'], data['version_major'],
            data['version_minor'], data['version_build'],
            data['meta'], data['bit_type']
            )
        if system_info:
            try:
                session.add(system_info)
                session.commit()
                print "system info was added"
                return system_info
            except Exception as e:
                session.rollback()
                print "BOOOH system info was not added"


def addSoftwareUpdate(session, data):
    session = validateSession(session)
    exists, operation = operationExists(session, data['operation_id'])
    node_id = exists.node_id
    if exists:
        operation.update({'results_received' : datetime.now()})
        session.commit()
        for update in data['data']:
            update_exists = updateExists(session, update['toppatch_id'])
            if not update_exists:
                if not 'kb' in update:
                    update['kb'] = None
                if not 'version' in update:
                    update['version'] = None
                software_update = Package(update['toppatch_id'],
                        update['kb'], update['version'],
                        update['vendor_id'],update['name'],
                        update['description'], update['support_url'],
                        update['severity'], dateParser(update['date_published']),
                        update['file_size']
                        )
                if software_update:
                    try:
                        session.add(software_update)
                        session.commit()
                    except:
                        session.rollback()

def addUpdatePerNode(session, data):
    session = validateSession(session)
    exists, operation = operationExists(session, data['operation_id'])
    if exists:
        node_id = exists.node_id
        node = session.query(SystemInfo).filter(SystemInfo.node_id == node_id).first()
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
                if node.os_code == "linux":
                    node_update = PackagePerNode(node_id,
                        addupdate['toppatch_id'], date_installed, 
                        hidden, installed=installed, is_linux=True
                        )
                elif node.os_code == "windows":
                    node_update = PackagePerNode(node_id,
                        addupdate['toppatch_id'], date_installed, 
                        hidden, installed=installed, is_windows=True
                        )
                elif node.os_code == "mac":
                    node_update = PackagePerNode(node_id,
                        addupdate['toppatch_id'], date_installed, 
                        hidden, installed=installed, is_mac=True
                        )
                elif node.os_code == "bsd":
                    node_update = PackagePerNode(node_id,
                        addupdate['toppatch_id'], date_installed, 
                        hidden, installed=installed, is_bsd=True
                        )
                elif node.os_code == "unix":
                    node_update = PackagePerNode(node_id,
                        addupdate['toppatch_id'], date_installed, 
                        hidden, installed=installed, is_unix=True
                        )
                try:
                    session.add(node_update)
                    session.commit()
                except:
                    session.rollback()

def addSoftwareAvailable(session, data):
    session = validateSession(session)
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
    session = validateSession(session)
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

def removeTag(session, tagname):
    session = validateSession(session)
    tag_exists, tag = tagExists(session, tag_name=tagname)
    tag_stats = session.query(TagStats).\
                    filter(TagStats.tag_id == tag.id)
    if tag:
        try:
            tag_stats.delete()
            session.commit()
            tag_exists.delete()
            session.commit()
            return(True, "Tag %s was deleted" % (tagname), tag.id)
        except Exception as e:
            session.rollback()
            return(False, "Tag %s does not exists" % (tagname))

def removeAllNodesFromTag(session, tag_name):
    session = validateSession(session)
    tag_oper, tag = tagExists(session, tag_name)
    tags_per_node = \
            session.query(TagsPerNode, TagInfo).join(TagInfo).filter(TagInfo.tag == tag_name).all()
    if len(tags_per_node) > 0:
        nodes = map(lambda nodes: nodes[0].node_id, tags_per_node)
        try:
            tags_deleted = map(lambda nodes: session.delete(nodes[0]),
                    tags_per_node)
            session.commit()
            return(True, "Nodes %s were deleted from tag %s" % \
                    (nodes, tag_name), nodes)
        except Exception as e:
            session.rollback()
            return(False, "Nodes %s were not deleted from tag %s" % \
                    (nodes, tag_name), nodes)
    elif tag:
        return(True, "No nodes for this tag %s Tag" % \
            (tag_name), tag_name)
    else:
        return(False, "Tag %s does not exists" % (tag_name), tag_name)

def removeNodesFromTag(session, tag_name, nodes=[]):
    session = validateSession(session)
    nodes_completed = []
    nodes_failed = []
    for node in nodes:
        tags_per_node = \
            session.query(TagsPerNode, TagInfo).join(TagInfo).filter(TagInfo.tag == tag_name).filter(TagsPerNode.node_id == node).all()
        if len(tags_per_node) > 0:
            try:
                tags_deleted = map(lambda nodes: session.delete(nodes[0]), 
                        tags_per_node)
                session.commit()
                nodes_completed.append(node)
            except Exception as e:
                session.rollback()
                nodes_failed.append(node)
                return(False, "Nodes %s were not deleted from tag %s" % \
                        (nodes, tag_name), nodes)
        else:
            return(False, "Tag %s does not exist" % \
                (tag_name), tag_name)
    if len(nodes_failed) > 0 and len(node_completed) >0:
        return(True, "Nodes %s were deleted from tag %s and nodes % were not deleted" % \
                (nodes_completed, tag_name, nodes_failed), nodes)
    elif len(nodes_failed) > 0 and len(node_completed)  == 0:
        return(False, "Nodes %s were not deleted from tag %s" % \
                (nodes_failed, tag_name), nodes)
    elif len(nodes_completed) > 0 and len(nodes_failed)  == 0:
        return(True, "Nodes %s were deleted from tag %s" % \
                (nodes_completed, tag_name), nodes)

def removeTimeBlock(session, id=None, label=None, start_date=None, start_time=None):
    session = validateSession(session)
    tb_object, timeblock = timeBlockExists(session, id, label, start_date, start_time)
    print tb_object, timeblock
    if tb_object:
        object_deleted = False, "Time Block %s has not been deleted"\
                % (timeblock.name)
        try:
            tb_object.delete()
            object_deleted = True, "Time Block %s has been deleted"\
                    % (timeblock.name)
            session.commit()
        except Exception as e:
            session.rollback()
    return object_deleted

def updateOperationRow(session, oper_id, results_recv=None, oper_recv=None):
    session = validateSession(session)
    exists, operation = operationExists(session, oper_id)
    if exists and results_recv:
        operation.update({'results_received' : datetime.now()})
        session.commit()
    elif exists and oper_recv:
        operation.update({'operation_received' : datetime.now()})
        session.commit()

def updateNode(session, node_id):
    session = validateSession(session)
    exists, node = nodeExists(session, node_id=node_id)
    if exists:
        exists.update({'last_agent_update' : datetime.now(),
                      'last_node_update' : datetime.now(),
                      'agent_status' : True,
                      'host_status' : True
                      })
        session.commit()
        installed_oper = session.query(PackagePerNode).filter_by(installed=True).filter_by(node_id=node_id)
        installed = installed_oper.first()
        pending_oper = session.query(PackagePerNode).filter_by(pending=True).filter_by(node_id=node_id)
        pending = pending_oper.all()
        for i in pending:
            if installed and pending:
                i.pending=False
        session.commit()
    else:
        print "System Info for %s does not exist yet" % ( node_id )
    return node

def updateNodeStats(session, node_id):
    session = validateSession(session)
    nodeupdates = session.query(PackagePerNode).filter_by(node_id=node_id)
    patchesinstalled = nodeupdates.filter_by(installed=True).all()
    patchesuninstalled = nodeupdates.filter_by(installed=False).all()
    patchespending = nodeupdates.filter_by(pending=True).all()
    nodestats = session.query(NodeStats).filter_by(node_id=node_id)
    nodeexists = nodestats.first()
    if nodeexists:
        nodestats.update({"patches_installed" : len(patchesinstalled),
                         "patches_available" : len(patchesuninstalled),
                         "patches_pending" : len(patchespending)})
        session.commit()
    else:
        add_node_stats = NodeStats(node_id, len(patchesinstalled), \
                       len(patchesuninstalled), len(patchespending), 0)
        session.add(add_node_stats)
        session.commit()

def updateNetworkStats(session):
    session = validateSession(session)
    stats = session.query(PackagePerNode)
    totalinstalled = stats.filter_by(installed=True).all()
    totalnotinstalled = stats.filter_by(installed=False).all()
    totalpending = stats.filter_by(pending=True).all()
    networkstats = session.query(NetworkStats)
    networkstatsexists = networkstats.filter_by(id=1).first()
    if networkstatsexists:
        networkstats.update({"patches_installed" : len(totalinstalled),
                             "patches_available" : len(totalnotinstalled),
                             "patches_pending" : len(totalpending)})
        session.commit()
    else:
        network_sstats_init = NetworkStats(len(totalinstalled),
                              len(totalnotinstalled), len(totalpending), 0)
        session.add(network_sstats_init)
        session.commit()

def updateTagStats(session):
    session = validateSession(session)
    tags = session.query(TagInfo).all()
    if len(tags) > 0:
        for tag in tags:
            nodes = session.query(TagsPerNode).\
                filter(TagsPerNode.tag_id == tag.id).all()
            patchesinstalled = 0
            patchesuninstalled = 0
            patchespending = 0
            if len(nodes) > 0:
                for node in nodes:
                    nodeupdates = session.query(PackagePerNode).\
                            filter_by(node_id=node.node_id)
                    patchesinstalled = patchesinstalled + nodeupdates.\
                            filter_by(installed=True).count()
                    patchesuninstalled = patchesuninstalled + nodeupdates.\
                            filter_by(installed=False).count()
                    patchespending = patchespending + nodeupdates.\
                            filter_by(pending=True).count()
                tag_stats = session.query(TagStats).\
                    filter_by(tag_id=tag.id)
                tag_exists = tag_stats.first()
                if tag_exists:
                    tag_stats.update({"patches_installed" : patchesinstalled,
                                     "patches_available" : patchesuninstalled,
                                     "patches_pending" : patchespending})
                    session.commit()
                else:
                    add_tag_stats = TagStats(tag.id, patchesinstalled, \
                                   patchesuninstalled, patchespending, 0)
                    session.add(add_tag_stats)
                    session.commit()


def updateRebootStatus(session, node_id, oper_type):
    session = validateSession(session)
    node, node_exists = nodeExists(session, node_id=node_id)
    print node, node_exists, "OKKKOKOKKO"
    if node_exists:
        if oper_type == 'reboot':
            node.update({'reboot' : False,
                         'agent_status' : False})
            session.commit()

def addResults(session, data):
    session = validateSession(session)
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
            os_code = session.query(SystemInfo).filter_by(node_id=node_id).first().os_code
            update_exists, update_oper = nodeUpdateExists(session, node_id, msg['toppatch_id'], os=os_code)
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
                session.commit()
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
                updateNode(session, node_id)
                updateNetworkStats(session)
                session.commit()
                TcpConnect("127.0.0.1", "FUCK YOU", port=8080, secure=False)
                return results
            except:
                session.rollback()
