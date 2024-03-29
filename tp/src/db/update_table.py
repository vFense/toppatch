#!/usr/bin/env python

import logging
import logging.config
from datetime import datetime
from socket import gethostbyaddr
from models.base import Base
from models.packages import *
from models.node import *
from models.tagging import *
from models.user_acl import *
from models.scheduler import *
from utils.common import *
from db.client import *
from db.query_table import *
from networking.tcpasync import TcpConnect
from sqlalchemy import or_

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


def add_results_non_json(session, node_id=None, oper_id=None, error=None,
        toppatch_id=None, reboot=False, result=False,
        results_received=datetime.now(), username='system_user'):
    """
        Add a new entry in the results table in RV
        arguments below..
        session == SQLAlchemy Session
        data == the json message received from the agent
    """
    session = validate_session(session)
    operation = operation_exists(session, oper_id)
    results = None
    if result and type(result) != bool:
        if 'success' in result:
            result = True
        elif 'failed' in result:
            result = False
    print result
    if oper_id and node_id and operation:
        results = Results(node_id=node_id, operation_id=oper_id, 
                succeeded=result, error=error,
                results_received=results_received
                )
    elif oper_id and not node_id and operation:
        results = Results(operation_id=oper_id,
                succeeded=result, error=error,
                results_received=results_received
                )
    if results:
        try:
            session.add(results)
            session.commit()
            if toppatch_id:
                patch_results = PatchResults(
                        results_id=results.id,
                        patch_id=toppatch_id, reboot=reboot
                        )
                try:
                    session.add(patch_results)
                    session.commit()
                except Exception as e:
                    print e
                    session.rollback()
            return(results)
        except Exception as e:
            print e
            session.rollback()
            return(None)


def add_node(session, client_ip=None, agent_timestamp=None,
        node_timestamp=None, host_name=None, display_name=None,
        computer_name=None, username='system_user'):
    """Add a node to the database"""
    session = validate_session(session)
    if not host_name and client_ip:
        try:
            host_name = gethostbyaddr(client_ip)[0]
        except:
            host_name = None
    try:
        addnode = NodeInfo(ip_address=client_ip, host_name=host_name,
            display_name=display_name, computer_name=computer_name,
            host_status=True, agent_status=True,
            last_agent_update=agent_timestamp,
            last_node_update=node_timestamp)
        session.add(addnode)
        session.commit()
        logger.info('%s - node %s added to node_info' %
                (username, client_ip)
                )
        return addnode
    except Exception as e:
        session.rollback()
        logger.error('node %s could not be added to node_info:%s' %
                (client_ip, e)
		)


def add_group(session, groupname=None):
    session = validate_session(session)
    if groupname:
        group_exists = session.query(Group).\
                filter(Group.groupname == groupname).first()
        if not group_exists:
            group = Group(groupname=groupname)
            try:
                session.add(group)
                session.commit()
                return({
                    'pass': True,
                    'message': 'Group %s added' % (groupname),
                    'id': group.id
                    })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': e
                    })
        else:
            return({
                'pass': False,
                'message': '%s already exists' %\
                        (group_exists.id)
                })

    else:
        return({
            'pass': False,
            'message': 'Need to pass the group_id'
            })


def add_user_to_group(session, user_id=None, group_id=None):
    session = validate_session(session)
    if user_id and group_id:
        group_for_user_exists = session.query(UsersInAGroup).\
                filter(UsersInAGroup.user_id == user_id).\
                filter(UsersInAGroup.group_id == group_id).\
                first()
        if not group_for_user_exists:
            add_user = UsersInAGroup(user_id, group_id)
            try:
                session.add(add_user)
                session.commit()
                return({
                    'pass': True,
                    'message': '%s added to %s' %\
                            (user_id, group_id)
                        })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': e
                    })
        else:
            return({
                'pass': False,
                'message': '%s already in this group %s' %\
                        (user_id, group_id)
                })
    else:
        return({
            'pass': False,
            'message': 'Need to pass the user_id and group_id'
            })



def add_global_user_acl(session, user_id=None, is_admin=False,
        is_global=True, allow_read=False, allow_install=False,
        allow_uninstall=False, allow_reboot=False, allow_schedule=False,
        allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False, deny_all=False,
        date_created=datetime.now(), date_modified=datetime.now(),
        username='system_user'
        ):
    """
        Add a Global User ACL to the database
    """
    session = validate_session(session)
    date_created=datetime.now()
    user_exists = session.query(GlobalUserAccess).\
            filter_by(user_id=user_id).first()
    if user_id and not user_exists:
        try:
            add_acl = GlobalUserAccess(user_id=user_id, is_admin=is_admin,
                    is_global=is_global, allow_read=allow_read,
                    allow_install=allow_install,
                    allow_uninstall=allow_uninstall, allow_reboot=allow_reboot,
                    allow_schedule=allow_schedule, allow_wol=allow_wol,
                    allow_snapshot_creation=allow_snapshot_creation,
                    allow_snapshot_removal=allow_snapshot_removal,
                    allow_snapshot_revert=allow_snapshot_revert,
                    allow_tag_creation=allow_tag_creation,
                    allow_tag_removal=allow_tag_removal, deny_all=deny_all,
                    date_created=date_created, date_modified=date_modified
                    )
            session.add(add_acl)
            session.commit()
            return({
                'pass': True,
                'message': 'User ACL was added for %s' % (user_id)
                })
        except Exception as e:
            session.rollback()
            return({
                'pass': False,
                'message': 'Failed to add ACL for user %s: %s' % \
                        (user_id, e)
                })
    elif user_id and user_exists:
        return({
            'pass': False,
            'message': 'Failed to add ACL for user %s: %s' % \
                    (user_id, 'User ACL already Exists')
            })


def add_global_group_acl(session, group_id=None, is_admin=False,
        is_global=True, allow_read=False, allow_install=False,
        allow_uninstall=False, allow_reboot=False, allow_schedule=False,
        allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False, deny_all=False,
        date_created=datetime.now(), date_modified=datetime.now(),
        username='system_user'
        ):
    """
        Add a Global Group ACL to the database
    """
    session = validate_session(session)
    date_created=datetime.now()
    group_exists = session.query(GlobalGroupAccess).\
            filter(GlobalGroupAccess.group_id == group_id).first()
    if group_id and not group_exists:
        try:
            add_acl = GlobalGroupAccess(group_id=group_id, is_admin=is_admin,
                    is_global=is_global, allow_read=allow_read,
                    allow_install=allow_install,
                    allow_uninstall=allow_uninstall, allow_reboot=allow_reboot,
                    allow_schedule=allow_schedule, allow_wol=allow_wol,
                    allow_snapshot_creation=allow_snapshot_creation,
                    allow_snapshot_removal=allow_snapshot_removal,
                    allow_snapshot_revert=allow_snapshot_revert,
                    allow_tag_creation=allow_tag_creation,
                    allow_tag_removal=allow_tag_removal, deny_all=deny_all,
                    date_created=date_created, date_modified=date_modified
                    )
            session.add(add_acl)
            session.commit()
            return({
                'pass': True,
                'message': 'Group ACL %s added' % (group_id)
                })
        except Exception as e:
            session.rollback()
            return({
                'pass': False,
                'message': 'Failed to add ACL for Group %s: %s' % \
                        (group_id, e)
                })
    elif group_id and group_exists:
        return({
            'pass': False,
            'message': 'Failed to add ACL for Group %s: %s' % \
                    (group_id, 'Group ACL already exists')
            })


def add_node_user_acl(session, node_id=None, user_id=None, allow_read=False,
        allow_install=False, allow_uninstall=False, allow_reboot=False,
        allow_schedule=False, allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False,
        date_created=datetime.now(), date_modified=datetime.now(),
        username='system_user'
        ):
    """
        Add a User ACL to a node in the database
    """
    session = validate_session(session)
    date_created=datetime.now()
    user_for_node_exists = session.query(NodeUserAccess).\
            filter(NodeUserAccess.user_id == user_id).\
            filter(NodeUserAccess.node_id == node_id).first()
    if user_id and node_id and not user_for_node_exists:
        try:
            add_acl = NodeUserAccess(node_id, user_id=user_id,
                    allow_read=allow_read, allow_install=allow_install,
                    allow_uninstall=allow_uninstall, allow_reboot=allow_reboot,
                    allow_schedule=allow_schedule, allow_wol=allow_wol,
                    allow_snapshot_creation=allow_snapshot_creation,
                    allow_snapshot_removal=allow_snapshot_removal,
                    allow_snapshot_revert=allow_snapshot_revert,
                    allow_tag_creation=allow_tag_creation,
                    allow_tag_removal=allow_tag_removal,
                    date_created=date_created, date_modified=date_modified
                    )
            session.add(add_acl)
            session.commit()
            return({
                'pass': True,
                'message': 'User ACL %s added for Node %s' % \
                    (user_id, node_id)
                    })
        except Exception as e:
            session.rollback()
            return({
                'pass': False,
                'message': 'Failed to add ACL for User %s on Node %s:%s' % \
                    (user_id, node_id, e)
                    })


def add_node_group_acl(session, node_id=None, group_id=None, allow_read=False,
        allow_install=False, allow_uninstall=False, allow_reboot=False,
        allow_schedule=False, allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False,
        date_created=datetime.now(), date_modified=datetime.now(),
        username='system_user'
        ):
    """
        Add a Group ACL to a Node in the database
    """
    session = validate_session(session)
    date_created=datetime.now()
    group_for_node_exists = session.query(NodeGroupAccess).\
            filter_by(group_id=group_id).\
            filter_by(node_id=node_id).first()
    if node_id and group_id and not group_for_node_exists:
        try:
            add_acl = NodeGroupAccess(node_id, group_id=group_id,
                    allow_read=allow_read, allow_install=allow_install,
                    allow_uninstall=allow_uninstall, allow_reboot=allow_reboot,
                    allow_schedule=allow_schedule, allow_wol=allow_wol,
                    allow_snapshot_creation=allow_snapshot_creation,
                    allow_snapshot_removal=allow_snapshot_removal,
                    allow_snapshot_revert=allow_snapshot_revert,
                    allow_tag_creation=allow_tag_creation,
                    allow_tag_removal=allow_tag_removal,
                    date_created=date_created, date_modified=date_modified
                    )
            session.add(add_acl)
            session.commit()
            return({
                'pass': True,
                'message': 'Group ACL %s added for Node %s' % \
                    (group_id, node_id)
                    })
        except Exception as e:
            session.rollback()
            return({
                'pass': False,
                'message': 'Failed to add ACL for Group %s on Node %s:%s' % \
                    (group_id, node_id, e)
                    })



def add_tag_user_acl(session, tag_id=None, user_id=None, allow_read=False,
        allow_install=False, allow_uninstall=False, allow_reboot=False,
        allow_schedule=False, allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False,
        date_created=datetime.now(), date_modified=datetime.now(),
        username='system_user'
        ):
    """
        Add a User ACL to a Tag in the database
    """
    session = validate_session(session)
    date_created=datetime.now()
    user_for_tag_exists = session.query(TagUserAccess).\
            filter_by(user_id=user_id).\
            filter_by(tag_id=tag_id).first()
    if user_id and tag_id and not user_for_tag_exists:
        try:
            add_acl = TagUserAccess(tag_id, user_id=user_id,
                    allow_read=allow_read, allow_install=allow_install,
                    allow_uninstall=allow_uninstall, allow_reboot=allow_reboot,
                    allow_schedule=allow_schedule, allow_wol=allow_wol,
                    allow_snapshot_creation=allow_snapshot_creation,
                    allow_snapshot_removal=allow_snapshot_removal,
                    allow_snapshot_revert=allow_snapshot_revert,
                    allow_tag_creation=allow_tag_creation,
                    allow_tag_removal=allow_tag_removal,
                    date_created=date_created, date_modified=date_modified
                    )
            session.add(add_acl)
            session.commit()
            return({
                'pass': True,
                'message': 'User ACL %s added for Tag %s' % \
                    (user_id, tag_id)
                    })
        except Exception as e:
            session.rollback()
            return({
                'pass': False,
                'message': 'Failed to add ACL for User %s on Tag %s:%s' % \
                    (user_id, tag_id, e)
                    })


def add_tag_group_acl(session, tag_id=None, group_id=None, allow_read=False,
        allow_install=False, allow_uninstall=False, allow_reboot=False,
        allow_schedule=False, allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False,
        date_created=datetime.now(), date_modified=datetime.now(),
        username='system_user'
        ):
    """
        Add a Group ACL to a Tag in the database
    """
    session = validate_session(session)
    date_created=datetime.now()
    group_for_tag_exists = session.query(TagGroupAccess).\
            filter_by(group_id=group_id).\
            filter_by(tag_id=tag_id).first()
    if group_id and tag_id and not group_for_tag_exists:
        try:
            add_acl = TagGroupAccess(tag_id, group_id,
                    allow_read=allow_read, allow_install=allow_install,
                    allow_uninstall=allow_uninstall, allow_reboot=allow_reboot,
                    allow_schedule=allow_schedule, allow_wol=allow_wol,
                    allow_snapshot_creation=allow_snapshot_creation,
                    allow_snapshot_removal=allow_snapshot_removal,
                    allow_snapshot_revert=allow_snapshot_revert,
                    allow_tag_creation=allow_tag_creation,
                    allow_tag_removal=allow_tag_removal,
                    date_created=date_created, date_modified=date_modified
                    )
            session.add(add_acl)
            session.commit()
            return({
                'pass': True,
                'message': 'Group ACL %s added for Tag %s' % \
                    (group_id, tag_id)
                    })
        except Exception as e:
            session.rollback()
            return({
                'pass': False,
                'message': 'Failed to add ACL for Group %s on Tag %s:%s' % \
                    (group_id, tag_id, e)
                    })


def add_tag(session, tag_name, user_id=None, username='system_user'):
    """
        Add a tag to the database
    """
    session = validate_session(session)
    date_created=datetime.now()
    try:
        add_tag = TagInfo(tag_name, date_created, user_id)
        session.add(add_tag)
        session.commit()
        return(True, "Tag %s added" % (tag_name), add_tag)
    except Exception as e:
        session.rollback()
        return(False, "Tag %s failed to add" % (tag_name))


def add_dependency(session, data, username='system_user'):
    """
        Add a dependency to the corresponding toppatch_id
        into the database
    """
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
                user_id=None, username='system_user'):
    """
        Add a list of nodes to an existing tag
        into the database
        arguments....
        session == SQLAlchemy Session
        nodes = list of nodes
        tag_id = id of tag
        or
        tag_name = name of tag
    """
    session = validate_session(session)
    completed = False
    count = 0
    tag = None
    if not tag_id and tag_name:
        tag = tag_exists(session, tag_name=tag_name)
    elif tag_id and not tag_name:
        tag = tag_exists(session, tag_id=tag_id)
    if not tag and user_id:
        tag_added, tag_msg, tag = \
                add_tag(session, tag_name, user_id=user_id)
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
                  enabled=False, username='system_user'):
    """
        Add a new timeblock to RV.
        arguments below..
        session == SQLAlchemy Session
        label == The name of the timeblock that you added
        start_date == "12/1/2012"
        start_time == "09:00 PM"
        end_time == "11:00 PM"
        days == (days of the week in binary. Example Mon through Fri 0111110)
        end_date == Optional ("12/1/2012")
        span_end_date_time == Optional ("12/3/2012" 03:00 AM)
        span == False
        enabled == False
    """
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
        session.rollback()
        return(False, "Time Block Could Not Be Added", e)


def add_csr(session, client_ip, location, csr_name,
            signed=False, signed_date=False,
            username='system_user'):
    """
        Add a new Certificate Signed Request into RV
        arguments below..
        session == SQLAlchemy Session
        client_ip == "192.168.0.1"
        location == The directory location
        ("/opt/TopPatch/var/lib/ssl/client/csr/192.168.0.1.csr")
    """
    session = validate_session(session)
    try:
        add_csr = CsrInfo(csr_name, client_ip, location, signed, signed_date)
        session.add(add_csr)
        session.commit()
        return add_csr
    except Exception as e:
        session.rollback()


def add_cert(session, node_id, cert_id, cert_name,
            cert_location, cert_expiration, username='system_user'):
    """
        Add a new Signed Certificate into RV
        arguments below..
        session == SQLAlchemy Session
        node_id == 1 This is the id of the node that this cert belongs too.
        cert_id == 1 This is the id corresponding csr_id
        cert_location == The directory location
        ("/opt/TopPatch/var/lib/ssl/client/keys/192.168.0.1.cert")
    """
    session = validate_session(session)
    try:
        add_cert = SslInfo(node_id, cert_id, cert_name,
                    cert_location, cert_expiration)
        session.add(add_cert)
        session.commit()
        return add_cert
    except Exception as e:
        session.rollback()


def add_operation(session, node_id, operation, operation_sent=None,
        operation_received=None, username='system_user'):
    """
        Add a new Operation into RV
        arguments below..
        session == SQLAlchemy Session
        node_id == 1 The id of the node that this operation belongs too.
        operation == reboot|install|uninstall (The operation type)
    """
    session = validate_session(session)
    add_oper = Operations(node_id, operation, operation_sent,
            operation_received, username
            )
    if add_oper:
        session.add(add_oper)
        session.commit()
        return add_oper


def update_node_stats(session, node_id, username='system_user'):
    """
        update the stats of the node in the node_stats table in RV
        arguments below..
        session == SQLAlchemy Session
        node_id == the id of the node
    """
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


def update_network_stats(session, username='system_user'):
    """
        update the global stats in network_stats table in RV
        arguments below..
        session == SQLAlchemy Session
    """
    session = validate_session(session)
    rebootspending = session.query(NodeInfo).\
            filter(NodeInfo.reboot == True).count()
    agentsdown = session.query(NodeInfo).\
            filter(NodeInfo.agent_status == False).count()
    agentsup = session.query(NodeInfo).\
            filter(NodeInfo.agent_status == True).count()
    stats = session.query(PackagePerNode)
    totalinstalled = stats.group_by(PackagePerNode.toppatch_id).\
            filter_by(installed=True).count()
    totalnotinstalled = stats.group_by(PackagePerNode.toppatch_id).\
            filter_by(installed=False).count()
    totalpending = stats.group_by(PackagePerNode.toppatch_id).\
            filter_by(pending=True).count()
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


def update_tag_stats(session, username='system_user'):
    """
        update the global tag stats in tag_stats table in RV
        arguments below..
        session == SQLAlchemy Session
    """
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
            else:
                tag_exists = session.query(TagStats).\
                    filter_by(tag_id=tag.id).first()
                if tag_exists:
                    session.delete(tag_exists)
                    session.commit()


def add_system_info(session, data, node_info, username='system_user'):
    """
        Add the system information of an existing node
        arguments below..
        session == SQLAlchemy Session
        data == this is the message that was sent by the agent and
        received by rvlistener.
        node_id == 1 The id of the node that this information belongs too.
    """
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = node_info.id

    if node_id:
        if 'computer_name' in data:
            node_info.computer_name = data['computer_name']
            session.commit()
        system_info = session.query(SystemInfo).\
                filter(SystemInfo.node_id == node_id).first()

        if system_info:
            system_info.os_code = data['os_code']
            system_info.os_string = data['os_string']
            system_info.version_minor = data['version_minor']
            system_info.version_build = data['version_build']
            system_info.meta = data['meta']
            system_info.bit_type = data['bit_type']
            try:
                session.commit()
            except Exception as e:
                session.rollback()
        else:
            system_info = SystemInfo(node_id, data['os_code'],
                data['os_string'], data['version_major'],
                data['version_minor'], data['version_build'],
                data['meta'], data['bit_type']
                )

            try:
                session.add(system_info)
                session.commit()

            except Exception as e:
                session.rollback()

        if 'hardware' in data:
            for key, values in data['hardware'].items():
                if 'nic' in key:
                    for network in values:
                        net_info = session.query(NetworkInterface).\
                            filter(NetworkInterface.node_id == node_id).\
                            filter(NetworkInterface.interface == \
                                    network['name']).first()

                        if net_info:
                            net_info.mac_address = network['mac']
                            net_info.ip_address = network['ip_address']
                            session.commit()

                        else:
                            net_info = NetworkInterface(node_id=node_id,
                                mac_address=network['mac'],
                                ip_address=network['ip_address'],
                                interface=network['name']
                                )
                            session.add(net_info)
                if 'storage' in key:
                    for storage in values:
                        storage_info = session.query(StorageInfo).\
                                filter(StorageInfo.node_id == node_id).\
                                filter(StorageInfo.name == storage['name']).\
                                first()

                        if storage_info:
                            storage_info.free_size_kb = storage['free_size_kb']
                            storage_info.size_kb = storage['size_kb']
                            session.commit()

                        else:
                            storage_info = StorageInfo(node_id=node_id,
                                free_size_kb=storage['free_size_kb'],
                                size_kb=storage['size_kb'],
                                file_system=storage['file_system'],
                                name=storage['name']
                                )
                            session.add(storage_info)
                if 'cpu' in key:
                    for cpu in values:
                        cpu_info = session.query(CpuInfo).\
                                filter(CpuInfo.node_id == node_id).\
                                filter(CpuInfo.name == cpu['cpu_id']).first()

                        if cpu_info:
                            cpu_info.speed_mhz = cpu['speed_mhz']
                            cpu_info.cores = cpu['cores']
                            cpu_info.cache_kb = cpu['cache_kb']
                            session.commit()

                        else:
                            cpu_info = CpuInfo(node_id=node_id,
                                cores=cpu['cores'],
                                speed_mhz=cpu['speed_mhz'],
                                bit_type=cpu['bit_type'],
                                cache_kb=cpu['cache_kb'],
                                name=cpu['name']
                                )
                            session.add(cpu_info)
                if 'display' in key:
                    for video in values:
                        video_info = session.query(DisplayInfo).\
                                filter(DisplayInfo.node_id == node_id).\
                                filter(DisplayInfo.name == video['name']).\
                                first()
                        if video_info:
                            video_info.speed_mhz = video['speed_mhz']
                            video_info.ram_kb = video['ram_kb']
                            video_info.name = video['name']
                            session.commit()
                        else:
                            video_info = DisplayInfo(node_id=node_id,
                                speed_mhz=video['speed_mhz'],
                                ram_kb=video['ram_kb'],
                                name=video['name']
                                )
                            session.add(video_info)
                if 'memory' in key:
                    mem_info = session.query(MemoryInfo).\
                                filter(MemoryInfo.node_id == node_id).\
                                first()
                    if mem_info:
                        mem_info.total_memory = values
                        session.commit()
                    else:
                        mem_info = MemoryInfo(
                                node_id=node_id,
                                total_memory=values
                                )
                        session.add(mem_info)

                try:
                    session.commit()
                except Exception as e:
                    print e, 'BAM'
                    session.rollback()

        return system_info


def add_software_update(session, data, username='system_user'):
    """
        Add software to the RV database, if the software does not exist.
        arguments below..
        session == SQLAlchemy Session
        data == this is the message that was sent by the agent and
        received by rvlistener.
    """
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = data['node_id']
    if node_id:
        if operation:
            results = add_results_non_json(session, node_id=node_id,
                oper_id=data['operation_id'],
                result=True, results_received=datetime.now()
                )
        for update in data['data']:
            update_exists = package_exists(session, update['toppatch_id'])
            if not update_exists:
                if not 'kb' in update:
                    update['kb'] = None
                if not 'version' in update:
                    update['version'] = None
                app_update = Package(update['toppatch_id'],
                        update['version'], update['kb'],
                        update['vendor_id'], update['name'],
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

def add_software_per_node(session, data, username='system_user'):
    """
        Create a new entry in the packages_per_node table
        arguments below..
        session == SQLAlchemy Session
        data == this is the message that was sent by the agent and
        received by rvlistener.
    """
    session = validate_session(session)
    session.commit()
    operation = operation_exists(session, data['operation_id'])
    node_id = data['node_id']
    if node_id:
        node = session.query(SystemInfo).\
                filter(SystemInfo.node_id == node_id).first()
        if operation:
            results = add_results_non_json(session, node_id=node_id,
                oper_id=data['operation_id'],
                result=True, results_received=datetime.now()
                )
        for addupdate in data['data']:
            update_exists = node_package_exists(session, node_id,
                    addupdate['toppatch_id'])
            if 'date_installed' in addupdate:
                date_installed = date_parser(addupdate['date_installed'])
            else:
                date_installed = None
            hidden = return_bool(addupdate['hidden'])
            installed = return_bool(addupdate['installed'])
            if not update_exists:
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
                elif node.os_code == "darwin":
                    node_update = PackagePerNode(node_id,
                        addupdate['toppatch_id'], date_installed,
                        hidden, installed=installed, is_darwin=True
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
                except Exception as e:
                    session.rollback()
            else:
                try:
                    update_exists.installed = installed
                    update_exists.hidden = hidden
                    update_exists.date_installed = date_installed
                    session.commit()
                except Exception as e:
                    session.rollback()
        update_node_stats(session, node_id)
        update_tag_stats(session, node_id)
        update_network_stats(session, node_id)


def add_software_available(session, data, username='system_user'):
    """
        Create a new entry in the software_available table
        This table is as of right now, strictly for Windows 3rd
        party applications
        arguments below..
        session == SQLAlchemy Session
        data == this is the message that was sent by the agent and
        received by rvlistener.
    """
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = data['node_id']
    if node_id:
        if operation:
            results = add_results_non_json(session, node_id=node_id,
                oper_id=data['operation_id'],
                result=True, results_received=datetime.now()
                )
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


def add_software_installed(session, data, username='system_user'):
    """
        Create a new entry in the software_installed table
        This table is a foreignKey to an existing row in
        software_available for a node.
        This table is as of right now, strictly for Windows 3rd
        party applications
        arguments below..
        session == SQLAlchemy Session
        data == this is the message that was sent by the agent and
        received by rvlistener.
    """
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node_id = data['node_id']
    if node_id:
        if operation:
            results = add_results_non_json(session, node_id=node_id,
                oper_id=data['operation_id'],
                result=True, results_received=datetime.now()
                )
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


def remove_acl(session, acl_type, user_id=None,
        group_id=None, tag_id=None, node_id=None):
    session = validate_session(session)
    acl = None
    if 'global_user' in acl_type and user_id:
        acl = session.query(GlobalUserAccess).\
                filter(GlobalUserAccess.user_id == user_id).first()
    elif 'global_group' in acl_type and group_id:
        acl = session.query(GlobalGroupAccess).\
                filter(GlobalGroupAccess.group_id == group_id).first()
    elif 'node_user' in acl_type and user_id and node_id:
        acl = session.query(NodeUserAccess).\
                filter(NodeUserAccess.user_id == user_id).\
                filter(NodeUserAccess.node_id == node_id).first()
    elif 'node_group' in acl_type and group_id and node_id:
        acl = session.query(NodeGroupAccess).\
                filter(NodeGroupAccess.group_id == group_id).\
                filter(NodeGroupAccess.node_id == node_id).first()
    elif 'tag_user' in acl_type and user_id and tag_id:
        acl = session.query(TagUserAccess).\
                filter(TagUserAccess.user_id == user_id).\
                filter(TagUserAccess.tag_id == tag_id).first()
    elif 'tag_group' in acl_type and group_id and tag_id:
        acl = session.query(TagGroupAccess).\
                filter(TagGroupAccess.group_id == group_id).\
                filter(TagGroupAccess.tag_id == tag_id).first()
    if acl:
        try:
            session.delete(acl)
            session.commit()
            return({
                'pass': True,
                'message': 'ACL deleted'
                })
        except Exception as e:
            session.rollback()
            return({
                'pass': False,
                'message': 'ACL could not be deleted'
                })
    else:
        return({
            'pass': False,
            'message': 'Not a valid ACL'
            })

def remove_tag(session, tagname, username='system_user'):
    """
        Remove a tag from the database
        arguments below..
        session == SQLAlchemy Session
        tagname == name of the tag you want to remove
    """
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


def remove_all_nodes_from_tag(session, tagname, username='system_user'):
    """
        Remove all nodes from a tag in the database
        arguments below..
        session == SQLAlchemy Session
        tag_name == name of the tag you want to remove
    """
    session = validate_session(session)
    tag = tag_exists(session, tag_name=tagname)
    if not tag:
        return(False, "Tag %s does not exists" % (tagname), tagname)
    tags_per_node = \
            session.query(TagsPerNode, TagInfo).\
                    join(TagInfo).\
                    filter(TagInfo.tag == tagname).all()
    if len(tags_per_node) > 0:
        nodes = map(lambda nodes: nodes[0].node_id, tags_per_node)
        try:
            tags_deleted = map(lambda nodes: session.delete(nodes[0]),
                    tags_per_node)
            session.commit()
            return(True, "Nodes %s were deleted from tag %s" % \
                    (nodes, tagname), nodes)
        except Exception as e:
            session.rollback()
            return(False, "Nodes %s were not deleted from tag %s" % \
                    (nodes, tagname), nodes)
    else:
        return(True, "No nodes for this tag %s Tag" % \
            (tagname), tagname)


def remove_nodes_from_tag(session, tag_name, nodes=[], username='system_user'):
    """
        Remove a node from a tag in the database
        arguments below..
        session == SQLAlchemy Session
        tag_name == name of the tag you want to remove
        nodes == list of nodes to be removed
    """
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
            start_date=None, start_time=None, username='system_user'):
    """
        Remove a timeblock from the database
        arguments below..
        session == SQLAlchemy Session
        id == the id of the timeblock
        label == the name of the timeblock
    """
    session = validate_session(session)
    timeblock = time_block_exists(session, id,
            label, start_date, start_time)
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


def update_operation_row(session, oper_id,
        oper_recv=None,
        username='system_user'):
    """
        update an existing operation in the RV database
        arguments below..
        session == SQLAlchemy Session
        oper_id == the id of the operation
    """
    session = validate_session(session)
    operation = operation_exists(session, oper_id)
    if operation and oper_recv:
        operation.operation_received = datetime.now()
        session.commit()


def update_node(session, node_id, ipaddress, username='system_user'):
    """
        update an existing node in the RV database
        arguments below..
        session == SQLAlchemy Session
        node_id == the id of the node
        ipaddress == The ipaddress of the node
    """
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
    return node

def update_reboot_status(session, node_id, oper_type, username='system_user'):
    """
        update the reboot status on a node in the node_info table in RV
        arguments below..
        session == SQLAlchemy Session
        node_id == The node_id of the node
        oper_type == "reboot"
    """
    session = validate_session(session)
    node = node_exists(session, node_id=node_id)
    if node:
        if oper_type == 'reboot':
            try:
                node.reboot = False
                node.agent_status = False
                session.commit()
            except Exception as e:
                session.rollback()


def update_global_user_acl(session, user_id=None, is_admin=False,
        is_global=True, allow_read=False, allow_install=False,
        allow_uninstall=False, allow_reboot=False, allow_schedule=False,
        allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False, deny_all=False,
        date_modified=datetime.now(), username='system_user'
        ):
    """
        Modify the Global ACL of a User in the database
    """
    session = validate_session(session)
    user = None
    if user_id:
        try:
            user = session.query(GlobalUserAccess).\
                    filter(GlobalUserAccess.user_id == user_id).first()
        except Exception as e:
            pass
        if user:
            try:
                user.is_admin = is_admin
                user.is_global = is_global
                user.allow_read = allow_read
                user.allow_install = allow_install
                user.allow_uninstall = allow_uninstall
                user.allow_reboot = allow_reboot
                user.allow_schedule = allow_schedule
                user.allow_wol = allow_wol
                user.allow_snapshot_creation = allow_snapshot_creation
                user.allow_snapshot_removal = allow_snapshot_removal
                user.allow_snapshot_revert = allow_snapshot_revert
                user.allow_tag_creation = allow_tag_creation
                user.allow_tag_removal = allow_tag_removal
                user.deny_all = deny_all
                user.date_modified = date_modified
                session.commit()
                return({
                    'pass': True,
                    'message': 'User ACL %s modified' % (user_id)
                    })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'Failed to modify ACL for user %s' % (user_id)
                    })
    else:
        return({
            'pass': False,
            'message': 'Invalid user_id %s' % (user_id)
            })


def update_global_group_acl(session, group_id=None, is_admin=False,
        is_global=True, allow_read=False, allow_install=False,
        allow_uninstall=False, allow_reboot=False, allow_schedule=False,
        allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False, deny_all=False,
        date_modified=datetime.now(), username='system_user'
        ):
    """
        Modify the Global ACL of a Group in the database
    """
    session = validate_session(session)
    group = None
    if group_id:
        try:
            group = session.query(GlobalGroupAccess).\
                    filter(GlobalGroupAccess.group_id == group_id).first()
        except Exception as e:
            pass
        if group:
            try:
                group.is_admin = is_admin
                group.is_global = is_global
                group.allow_read = allow_read
                group.allow_install = allow_install
                group.allow_uninstall = allow_uninstall
                group.allow_reboot = allow_reboot
                group.allow_schedule = allow_schedule
                group.allow_wol = allow_wol
                group.allow_snapshot_creation = allow_snapshot_creation
                group.allow_snapshot_removal = allow_snapshot_removal
                group.allow_snapshot_revert = allow_snapshot_revert
                group.allow_tag_creation = allow_tag_creation
                group.allow_tag_removal = allow_tag_removal
                group.deny_all = deny_all
                group.date_modified = date_modified
                session.commit()
                return({
                    'pass': True,
                    'message': 'Group ACL %s modified' % (group_id)
                    })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'Failed to modify ACL for Group %s' % (group_id)
                    })
    else:
        return({
            'pass': False,
            'message': 'Invalid group_id %s' % (group_id)
            })



def update_node_user_acl(session, node_id=None, user_id=None,
        allow_install=False, allow_uninstall=False, allow_reboot=False,
        allow_schedule=False, allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False, allow_read=False,
        date_modified=datetime.now(), username='system_user'
        ):
    """
        modify the global permissions of a user on a node
        in the database
    """
    session = validate_session(session)
    user = None
    if user_id and node_id:
        user = session.query(NodeUserAccess).\
                filter(NodeUserAccess.user_id == user_id).\
                filter(NodeUserAccess.node_id == node_id).first()
        if user:
            try:
                user.allow_install = allow_install
                user.allow_uninstall = allow_uninstall
                user.allow_reboot = allow_reboot
                user.allow_schedule = allow_schedule
                user.allow_wol = allow_wol
                user.allow_snapshot_creation = allow_snapshot_creation
                user.allow_snapshot_removal = allow_snapshot_removal
                user.allow_snapshot_revert = allow_snapshot_revert
                user.allow_tag_creation = allow_tag_creation
                user.allow_tag_removal = allow_tag_removal
                user.allow_read = allow_read
                user.date_modified = date_modified
                session.commit()
                return({
                    'pass': True,
                    'message': 'ACL for User %s was modified for Node %s' % \
                            (user_id, node_id)
                            })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'Failed to modify ACL for User %s on Node %s' % \
                        (user_id, node_id)
                        })
    else:
        return({
            'pass': False,
            'message': 'Invalid user_id %s and or node_id %s' % \
                (user_id, node_id)
                })


def update_node_group_acl(session, node_id=None, group_id=None,
        allow_install=False, allow_uninstall=False, allow_reboot=False,
        allow_schedule=False, allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False, allow_read=False,
        date_modified=datetime.now(), username='system_user'
        ):
    """
        Modify the Global ACL of a Group on a node
        in the database
    """
    session = validate_session(session)
    group = None
    if group_id and node_id:
        group = session.query(NodeGroupAccess).\
                filter(NodeGroupAccess.group_id == group_id).\
                filter(NodeGroupAccess.node_id == node_id).first()
        if group:
            try:
                group.allow_install = allow_install
                group.allow_uninstall = allow_uninstall
                group.allow_reboot = allow_reboot
                group.allow_schedule = allow_schedule
                group.allow_wol = allow_wol
                group.allow_snapshot_creation = allow_snapshot_creation
                group.allow_snapshot_removal = allow_snapshot_removal
                group.allow_snapshot_revert = allow_snapshot_revert
                group.allow_tag_creation = allow_tag_creation
                group.allow_tag_removal = allow_tag_removal
                group.allow_read = allow_read
                group.date_modified = date_modified
                session.commit()
                return({
                    'pass': True,
                    'message': 'ACL for Group %s was modified for Node %s' % \
                        (group_id, node_id)
                        })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'Failed to modify ACL for Group %s on Node %s' % \
                        (group_id, node_id)
                        })
    else:
        return({
            'pass': False,
            'message': 'Invalid group_id %s and or node_id %s' % \
                (group_id, node_id)
                })


def update_tag_user_acl(session, tag_id=None, user_id=None,
        allow_install=False, allow_uninstall=False, allow_reboot=False,
        allow_schedule=False, allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False, allow_read=False,
        date_modified=datetime.now(),
        username='system_user'
        ):
    """
        Modify the Global ACL of a User on a Tag
        in the database
    """
    session = validate_session(session)
    user = None

    if user_id and tag_id:
        user = session.query(TagUserAccess).\
                filter(TagUserAccess.user_id == user_id).\
                filter(TagUserAccess.tag_id == tag_id).first()
        if user:
            try:
                user.allow_install = allow_install
                user.allow_uninstall = allow_uninstall
                user.allow_reboot = allow_reboot
                user.allow_schedule = allow_schedule
                user.allow_wol = allow_wol
                user.allow_snapshot_creation = allow_snapshot_creation
                user.allow_snapshot_removal = allow_snapshot_removal
                user.allow_snapshot_revert = allow_snapshot_revert
                user.allow_tag_creation = allow_tag_creation
                user.allow_tag_removal = allow_tag_removal
                user.allow_read = allow_read
                user.date_modified = date_modified
                session.commit()
                return({
                    'pass': True,
                    'message': 'ACL for User %s was modified for Tag %s' % \
                        (user_id, tag_id)
                        })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'Failed to modify ACL for User %s on Tag %s' % \
                        (user_id, tag_id)
                        })
    else:
        return({
            'pass': False,
            'message': 'Invalid user_id %s and or tag_id' % \
                (user_id, tag_id)
                })


def update_tag_group_acl(session, tag_id=None, group_id=None,
        allow_install=False, allow_uninstall=False, allow_reboot=False,
        allow_schedule=False, allow_wol=False, allow_snapshot_creation=False,
        allow_snapshot_removal=False, allow_snapshot_revert=False,
        allow_tag_creation=False, allow_tag_removal=False, allow_read=False,
        date_modified=datetime.now(), username='system_user'
        ):
    """
        Modify the Global ACL of a Group on a Tag
        in the database
    """
    session = validate_session(session)
    group = None

    if group_id and tag_id:
        group = session.query(TagGroupAccess).\
                filter(TagGroupAccess.group_id == group_id).\
                filter(TagGroupAccess.tag_id == tag_id).first()
        if group:
            try:
                group.allow_install = allow_install
                group.allow_uninstall = allow_uninstall
                group.allow_reboot = allow_reboot
                group.allow_schedule = allow_schedule
                group.allow_wol = allow_wol
                group.allow_snapshot_creation = allow_snapshot_creation
                group.allow_snapshot_removal = allow_snapshot_removal
                group.allow_snapshot_revert = allow_snapshot_revert
                group.allow_tag_creation = allow_tag_creation
                group.allow_tag_removal = allow_tag_removal
                group.allow_read = allow_read
                group.date_modified = date_modified
                session.commit()
                return({
                    'pass': True,
                    'message': 'ACL for Group %s was modified for Tag %s' % \
                        (group_id, tag_id)
                        })
            except Exception as e:
                session.rollback()
                return({
                    'pass': False,
                    'message': 'Failed to modify ACL for Group %s on Tag %s' % \
                        (group_id, tag_id)
                        })
    else:
        return({
            'pass': False,
            'message': 'Invalid group_id %s and or tag_id' % \
                (group_id, tag_id)
                })


def add_results(session, data, username='system_user'):
    """
        Add a new entry in the results table in RV
        arguments below..
        session == SQLAlchemy Session
        data == the json message received from the agent
    """
    session = validate_session(session)
    operation = operation_exists(session, data['operation_id'])
    node = node_exists(session,node_id=data['node_id'])
    if node:
        node_id = data['node_id']
        if data['operation'] == 'reboot':
            node.reboot = False
            session.commit()
        if not 'data' in data:
            if 'restart' in data['operation'] or \
                    'stop' in data['operation'] or \
                    'start' in data['operation']:
                results = add_results_non_json(session, node_id=node_id,
                        oper_id=data['operation_id'],
                        result=return_bool(data['result']),
                        error=data['error'],
                        results_received=datetime.now()
                        )
                return(results)

        for msg in data['data']:
            if 'reboot' in msg:
                reboot = return_bool(msg['reboot'])
            else:
               reboot = False
            os_code = session.query(SystemInfo).\
                    filter_by(node_id=node_id).first().os_code
            update_exists = node_package_exists(session, node_id, msg['toppatch_id'])
            if update_exists:
                if data['operation'] == "install" and msg['result'] == 'success':
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
                results = add_results_non_json(
                        session, node_id=node_id,
                        oper_id=data['operation_id'],
                        toppatch_id=msg['toppatch_id'],
                        result=msg['result'],
                        reboot=reboot, error=error,
                        results_received=datetime.now()
                        )
                update_node_stats(session, node_id)
                update_network_stats(session)
                update_tag_stats(session)
                session.commit()
        return results
