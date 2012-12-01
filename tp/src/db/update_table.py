#!/usr/bin/env python


from datetime import datetime
from socket import gethostbyaddr
from models.base import Base
from models.packages import *
from models.node import *
from models.tagging import *
from models.scheduler import *
from utils.common import *
from db.client import *
from db.query_table import *
from networking.tcpasync import TcpConnect


def add_node(session, client_ip, agent_timestamp=None, node_timestamp=None):
    """Add a node to the database"""
    session = validate_session(session)
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


def add_tag(session, tag_name, user_id=None):
    """Add a tag to the database"""
    session = validate_session(session)
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


def add_dependency(session, data):
    """Add a dependency to the corresponding toppatch_id
       into the database"""
    session = validate_session(session)
    failed_count = 0
    for deps in data['data']:
        pkg_id = deps['toppatch_id']
        for dep in deps['dependencies']:
            dep_exists = session.query(LinuxPackageDependency).\
                    filter(LinuxPackageDependency.toppatch_id == pkg_id).\
                    filter(LinuxPackageDependency.dependency == dep).first()
            if not dep_exists:
                try:
                    dep_add = LinuxPackageDependency(pkg_id, dep)
                    session.add(dep_add)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    failed_count += 1


def add_tag_per_node(session, nodes=[], tag_id=None, tag_name=None,
                user_id=None):
    session = validate_session(session)
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
            session.query(TagsPerNode).\
                    filter_by(node_id=node).\
                    filter_by(tag_id=tag.id).first()
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


def add_time_block(session, label, start_date, start_time, end_time,
                  days, end_date=None, span_end_date_time=None, span=False,
                  enabled=False):
    session = validate_session(session)
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


def add_csr(session, client_ip, location, csr_name,
            signed=False, signed_date=False):
    session = validate_session(session)
    try:
        add_csr = CsrInfo(csr_name, client_ip, location, signed, signed_date)
        session.add(add_csr)
        session.commit()
        return add_csr
    except Exception as e:
        session.rollback()
        print e


def add_cert(session, node_id, cert_id, cert_name,
            cert_location, cert_expiration):
    session = validate_session(session)
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

def add_operation(session, node_id, operation, result_id=None,
        operation_sent=None, operation_received=None, results_received=None):
    add_oper = Operations(node_id, operation, result_id,
            operation_sent, operation_received, results_received
            )
    session = validate_session(session)
    if add_oper:
        session.add(add_oper)
        session.commit()
        return add_oper


def add_system_info(session, data, node_info):
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = node_info.id
    if node_id:
        if operation:
            operation.results_received = datetime.now()
            session.commit()
        system_info = SystemInfo(node_id, data['os_code'],
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


def add_app_update(session, data):
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = data['node_id']
    if node_id:
        if operation:
            operation.results_received = datetime.now()
            session.commit()
        for update in data['data']:
            update_exists = updateExists(session, update['toppatch_id'])
            if not update_exists:
                if not 'kb' in update:
                    update['kb'] = None
                if not 'version' in update:
                    update['version'] = None
                app_update = Package(update['toppatch_id'],
                        update['kb'], update['version'],
                        update['vendor_id'],update['name'],
                        update['description'], update['support_url'],
                        update['severity'], date_parser(update['date_published']),
                        update['file_size']
                        )
                if app_update:
                    try:
                        session.add(app_update)
                        session.commit()
                    except:
                        session.rollback()

def add_update_per_node(session, data):
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = data['node_id']
    if node_id:
        node = session.query(SystemInfo).\
                filter(SystemInfo.node_id == node_id).first()
        if operation:
            operation.results_received = datetime.now()
            session.commit()
        for addupdate in data['data']:
            update_exists = node_update_exists(session, node_id,
                    addupdate['toppatch_id'])
            if not update_exists:
                if 'date_installed' in addupdate:
                    date_installed = date_parser(addupdate['date_installed'])
                else:
                    date_installed = None
                hidden = return_bool(addupdate['hidden'])
                installed = return_bool(addupdate['installed'])
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


def add_software_available(session, data):
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = data['node_id']
    if node_id:
        if operation:
            operation.results_received = datetime.now()
            session.commit()
        for software in data['data']:
            app_exists = software_exists(session, software['name'],
                    software['version'])
            if not app_exists:
                app_update = SoftwareAvailable(node_id,
                            software['name'], software['vendor'],
                            software['version']
                            )
                try:
                    session.add(app_update)
                    session.commit()
                except:
                    session.rollback()


def add_software_installed(session, data):
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = data['node_id']
    if node_id:
        if exists:
            operation.results_received = datetime.now()
            session.commit()
        for software in data['data']:
            app_exists = software_exists(session, software['name'],
                    software['version'])
            if app_exists:
                node_app_exists = node_software_exists(session,
                    app_exists.id)
                if not node_app_exists:
                    app_update = SoftwareInstalled(node_id,
                            app_exists.id
                            )
                    try:
                        session.add(app_update)
                        session.commit()
                    except:
                        session.rollback()


def remove_tag(session, tagname):
    session = validate_session(session)
    tag = tag_exists(session, tag_name=tagname)
    tagid= tag.id
    tag_stats = session.query(TagStats).\
            filter(TagStats.tag_id == tag.id)
    if tag:
        try:
            tag_stats.delete()
            session.commit()
            session.delete(tag)
            session.commit()
            return(True, "Tag %s was deleted" % (tagname), tagid)
        except Exception as e:
            session.rollback()
            return(False, "Tag %s does not exists" % (tagname))


def remove_all_nodes_from_tag(session, tag_name):
    session = validate_session(session)
    tag = tag_exists(session, tag_name)
    if not tag:
        return(False, "Tag %s does not exists" % (tag_name), tag_name)
    tags_per_node = \
            session.query(TagsPerNode, TagInfo).\
                    join(TagInfo).\
                    filter(TagInfo.tag == tag_name).all()
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
    else:
        return(True, "No nodes for this tag %s Tag" % \
            (tag_name), tag_name)


def remove_nodes_from_tag(session, tag_name, nodes=[]):
    session = validate_session(session)
    nodes_completed = []
    nodes_failed = []
    for node in nodes:
        tags_per_node = \
            session.query(TagsPerNode, TagInfo).\
                    join(TagInfo).filter(TagInfo.tag == tag_name).\
                    filter(TagsPerNode.node_id == node).all()
        if len(tags_per_node) > 0:
            try:
                tags_deleted = map(lambda nodes: session.delete(nodes[0]), 
                        tags_per_node)
                session.commit()
                nodes_completed.append(node)
            except Exception as e:
                session.rollback()
                nodes_failed.append(node)
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


def remove_time_block(session, id=None, label=None,
            start_date=None, start_time=None):
    session = validate_session(session)
    timeblock = time_block_exists(session, id,
            label, start_date, start_time)
    print timeblock
    if timeblock:
        object_deleted = False, "Time Block %s has not been deleted"\
                % (timeblock.name)
        try:
            session.delete(timeblock)
            object_deleted = True, "Time Block %s has been deleted"\
                    % (timeblock.name)
            session.commit()
        except Exception as e:
            session.rollback()
    return object_deleted


def update_operation_row(session, oper_id, results_recv=None,
            oper_recv=None):
    session = validate_session(session)
    operation = operation_exists(session, oper_id)
    if operation and results_recv:
        operation.results_received = datetime.now()
        session.commit()
    elif operation and oper_recv:
        operation.operation_received = datetime.now()
        session.commit()


def update_node(session, node_id, ipaddress):
    session = validate_session(session)
    node = node_exists(session, node_id=node_id)
    error = None
    if not node.ip_address == ipaddress:
        try:
            node.ip_address = ipaddress
            session.commit()
        except Exception as e:
            session.rollback()
            error = e.message
            print error
    if node:
        node.last_agent_update = datetime.now()
        node.last_node_update = datetime.now()
        node.agent_status = True
        node.host_status = True
        session.commit()
        installed_oper = session.query(PackagePerNode).\
                filter_by(installed=True).filter_by(node_id=node_id)
        installed = installed_oper.first()
        pending_oper = session.query(PackagePerNode).\
                filter_by(pending=True).filter_by(node_id=node_id)
        pending = pending_oper.all()
        for i in pending:
            if installed and pending:
                i.pending=False
        session.commit()
    else:
        print "System Info for %s does not exist yet" % ( node_id )
    return node


def update_node_stats(session, node_id):
    session = validate_session(session)
    rebootspending = session.query(NodeInfo).\
            filter(NodeInfo.reboot == True).\
            filter(NodeInfo.id == node_id).count()
    agentsdown = session.query(NodeInfo).\
            filter(NodeInfo.agent_status == False).\
            filter(NodeInfo.id == node_id).count()
    agentsup = session.query(NodeInfo).\
            filter(NodeInfo.agent_status == True).\
            filter(NodeInfo.id == node_id).count()
    nodeupdates = session.query(PackagePerNode).filter_by(node_id=node_id)
    patchesinstalled = nodeupdates.filter_by(installed=True).count()
    patchesuninstalled = nodeupdates.filter_by(installed=False).count()
    patchespending = nodeupdates.filter_by(pending=True).count()
    nodestats = session.query(NodeStats).filter_by(node_id=node_id)
    node_exist = nodestats.first()
    if node_exist:
        nodestats.update({"patches_installed" : patchesinstalled,
                         "patches_available" : patchesuninstalled,
                         "patches_pending" : patchespending,
                         "reboots_pending" : rebootspending,
                         "agents_down" : agentsdown,
                         "agents_up" : agentsup})
        session.commit()
    else:
        add_node_stats = NodeStats(node_id, patchesinstalled,
                       patchesuninstalled, patchespending, 0,
                       rebootspending, agentsdown, agentsup)
        session.add(add_node_stats)
        session.commit()


def update_network_stats(session):
    session = validate_session(session)
    rebootspending = session.query(NodeInfo).\
            filter(NodeInfo.reboot == True).count()
    agentsdown = session.query(NodeInfo).\
            filter(NodeInfo.agent_status == False).count()
    agentsup = session.query(NodeInfo).\
            filter(NodeInfo.agent_status == True).count()
    stats = session.query(PackagePerNode)
    totalinstalled = stats.filter_by(installed=True).count()
    totalnotinstalled = stats.filter_by(installed=False).count()
    totalpending = stats.filter_by(pending=True).count()
    networkstats = session.query(NetworkStats)
    networkstatsexists = networkstats.filter_by(id=1).first()
    if networkstatsexists:
        networkstats.update({"patches_installed" : totalinstalled,
                             "patches_available" : totalnotinstalled,
                             "patches_pending" : totalpending,
                             "reboots_pending" : rebootspending,
                             "agents_down" : agentsdown,
                             "agents_up" : agentsup})
        session.commit()
    else:
        network_sstats_init = NetworkStats(totalinstalled,
                              totalnotinstalled, totalpending, 0,
                              rebootspending, agentsdown, agentsup)
        session.add(network_sstats_init)
        session.commit()


def update_tag_stats(session):
    session = validate_session(session)
    tags = session.query(TagInfo).all()
    if len(tags) > 0:
        for tag in tags:
            nodes = session.query(TagsPerNode).\
                filter(TagsPerNode.tag_id == tag.id).all()
            patchesinstalled = 0
            patchesuninstalled = 0
            patchespending = 0
            rebootspending = 0
            agentsdown = 0
            agentsup = 0
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
                    rebootspending = rebootspending + \
                            session.query(NodeInfo).\
                            filter(NodeInfo.id == node.node_id).\
                            filter(NodeInfo.reboot == True).count()
                    agentsdown = agentsdown + \
                            session.query(NodeInfo).\
                            filter(NodeInfo.id == node.node_id).\
                            filter(NodeInfo.agent_status == False).count()
                    agentsup = agentsup + \
                            session.query(NodeInfo).\
                            filter(NodeInfo.id == node.node_id).\
                            filter(NodeInfo.agent_status == True).count()
                tag_stats = session.query(TagStats).\
                    filter_by(tag_id=tag.id)
                tag_exists = tag_stats.first()
                if tag_exists:
                    tag_stats.update({"patches_installed" : patchesinstalled,
                                     "patches_available" : patchesuninstalled,
                                     "patches_pending" : patchespending,
                                     "patches_pending" : patchespending,
                                     "reboots_pending" : rebootspending,
                                     "agents_down" : agentsdown,
                                     "agents_up" : agentsup})
                    session.commit()
                else:
                    add_tag_stats = TagStats(tag.id, patchesinstalled,
                                   patchesuninstalled, patchespending, 0,
                                   rebootspending, agentsdown, agentsup)
                    session.add(add_tag_stats)
                    session.commit()


def update_reboot_status(session, node_id, oper_type):
    session = validate_session(session)
    node = node_exists(session, node_id=node_id)
    print node, "OKKKOKOKKO"
    if node:
        if oper_type == 'reboot':
            node.reboot = False,
            node.agent_status = False
            session.commit()


def add_results(session, data):
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node = node_exists(session,node_id=data['node_id'])
    print node
    if node:
        node_id = data['node_id']
        if data['operation'] == 'reboot':
            node.reboot = False
            session.commit()
        for msg in data['data']:
            print msg
            if 'reboot' in msg:
                reboot = return_bool(msg['reboot'])
            else:
               reboot = None
            os_code = session.query(SystemInfo).\
                    filter_by(node_id=node_id).first().os_code
            update_exists = node_update_exists(session, node_id, msg['toppatch_id'])
            if update_exists:
                if data['operation'] == "install" and msg['result'] == 'success':
                    print "patch installed on %s %s" % ( node_id, msg['toppatch_id'] )
                    update_exists.installed = True
                    update_exists.date_installed = datetime.now()
                    update_exists.pending = False
                    if reboot:
                        if node.reboot == False:
                            node.reboot = reboot
                elif data['operation'] == "install" and msg['result'] == 'failed':
                    update_exists.installed = False
                    update_exists.date_installed = datetime.now()
                    update_exists.pending = False
                    if reboot:
                        if node.reboot == False:
                            node.reboot = reboot
                elif data['operation'] == "uninstall" and msg['result'] == 'success':
                    print "deleting patch from managed_windows_updates %s on node_id %s" % ( msg['toppatch_id'], node_id )
                    update_exists.installed = False
                    update_exists.pending = False
                    if reboot:
                        if node.reboot == False:
                            node.reboot = reboot
                elif data['operation'] == "uninstall" and msg['result'] == 'failed':
                    update_exists.update({'installed' : True, 'date_installed' : datetime.now()})
                    if reboot:
                        if node.reboot == False:
                            node.reboot = reboot
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
                if operation:
                    operation.results_id = results.id
                    operation.results_received = datetime.now()
                update_node_stats(session, node_id)
                update_network_stats(session)
                session.commit()
                TcpConnect("127.0.0.1", "FUCK YOU", port=8080, secure=False)
                return results
            except:
                session.rollback()
