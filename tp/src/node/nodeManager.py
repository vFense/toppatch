#!/usr/bin/env python

import logging, logging.config
from db.update_table import *
from db.client import validate_session
from utils.common import *
from models.node import *
from models.packages import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

def change_display_name(session, nodeid=None, displayname=None, username='system_user'):
    session = validate_session(session)
    result = None
    if nodeid and displayname:
        node = session.query(NodeInfo).\
            filter(NodeInfo.id == nodeid).first()
        if node:
            try:
                if re.search(r'none', displayname, re.IGNORECASE):
                    displayname = return_bool(displayname)
                node.display_name = displayname
                session.commit()
                logger.info('%s - Display name was changed to %s' %
                            (username, displayname)
                )
                result = {
                    'pass' : True,
                    'message' : 'Display name change to %s' %
                            (displayname)
                    }
            except Exception as e:
                session.rollback()
                logger.error('%s - Display name was not changed to %s' %
                            (username, displayname)
                        )
                result = {
                    'pass' : False,
                    'message' : "Display name was not changed to %s"%
                            (displayname)
                        }
        else:
            result = {
                'pass': False,
                'message': 'Node doesnt exist'
                }
    else:
        result = {
            'pass': False,
            'message': 'Incorrect parameters passed'
            }
    return(result)

  
def change_host_name(session, nodeid=None, hostname=None, username='system_user'):
    session = validate_session(session)
    result = None
    if nodeid and hostname:
        node = session.query(NodeInfo).\
            filter(NodeInfo.id == nodeid).first()
        if node:
            try:
                if re.search(r'none', hostname, re.IGNORECASE):
                    hostname = return_bool(hostname)
                node.host_name = hostname
                session.commit()
                logger.info('%s - Host name was changed to %s' %
                            (username, hostname)
                        )
                result = {
                     'pass' : True,
                     'message' : 'Host name change to %s' %
                             (hostname)
                     }
            except Exception as e:
                session.rollback()
                logger.error('%s - Host name was not changed to %s' %
                            (username, hostname)
                            )
                result = {
                     'pass' : False,
                     'message' : 'Host name was not changed to %s' %
                             (hostname)
                     }
        else:
            result = {
                 'pass' : False,
                 'message' : 'Invalid node_id %s' %
                             (node_id)
                 }
    else:
        result = {
            'pass': False,
            'message': 'Incorrect parameters passed'
            }
    return(result)


def node_remover(session, node_id=None, certs=True,
        just_clean_and_not_delete=False,
        username='system_user'):
    session = validate_session(session)
    result = None
    if node_id:
        node = session.query(NodeInfo).\
            filter(NodeInfo.id == node_id).first()
        if node:
            try:
                session.query(Results).\
                    filter(Results.node_id == node.id).delete()
                session.commit()
                session.query(Operations).\
                    filter(Operations.node_id == node.id).delete()
                session.commit()
                session.query(PackagePerNode).\
                    filter(PackagePerNode.node_id == node.id).delete()
                session.commit()
                session.query(SoftwareInstalled).\
                    filter(SoftwareInstalled.node_id == node.id).delete()
                session.commit()
                session.query(SoftwareAvailable).\
                    filter(SoftwareAvailable.node_id == node.id).delete()
                session.commit()
                session.query(NodeStats).\
                    filter(NodeStats.node_id == node.id).delete()
                session.commit()
                session.query(NetworkInterface).\
                    filter(NetworkInterface.node_id == node.id).delete()
                session.commit()
                session.query(NodeUserAccess).\
                    filter(NodeUserAccess.node_id == node.id).delete()
                session.commit()
                session.query(SystemInfo).\
                    filter(SystemInfo.node_id == node_id).delete()
                session.commit()
                if not just_clean_and_not_delete:
                    ssl_info = session.query(SslInfo).\
                        filter(SslInfo.node_id == node.id).delete()
                    session.commit()
                    session.query(NodeInfo).\
                        filter(NodeInfo.id == node_id).delete()
                    session.commit()
                    session.query(CsrInfo).\
                        filter(CsrInfo.ip_address == node.ip_address).delete()
                    session.commit()
                    result = {
                        'pass': True,
                        'message': 'All information for %s has been deleted' %
                                (node.host_name,
                                'from RemediationVault, except for ssl_info'
                                )
                            }
                    logger.info('%s - Node %s was cleaned %s' %
                                (username, node.host_name,
                                'from RemediationVault, except for ssl_info'
                                )
                            )
                else:
                    result = {
                        'pass': True,
                        'message': '%s has been deleted from RemediationVault' %
                                (node.host_name)
                            }
                    logger.info('%s - Node %s was deleted from RemediationVault' %
                                (username, node.host_name)
                            )
            except Exception as e:
                result = {
                    'pass': False,
                    'message': '%s could not be deleted from %s. Error:%s' %
                        (node.host_name, 'RemediationVault', e)
                    }
                logger.info('%s - Node %s could not be deleted from %s' %
                            (username, node.host_name, 'RemediationVault')
                        )
        else:
            result = {
                'pass': False,
                'message': 'NodeID %s does not exist in RemediationVault' %
                    (node_id)
                }
            logger.info('%s - Node %s does not exist in %s' %
                        (username, node_id, 'RemediationVault')
                    )
    else:
        result = {
            'pass': False,
            'message': 'NodeID %s does not exist in RemediationVault' %
                (node_id)
            }
        logger.info('%s - Node %s does not exist in %s' %
                    (username, node_id, 'RemediationVault')
                )
    return(result)
                    
                    
def node_toggler(session, nodeid=None, toggle=False, username='system_user'):
    session = validate_session(session)
    result = None
    if nodeid:
        sslinfo = session.query(SslInfo).\
            filter(SslInfo.node_id == nodeid).first()
        if sslinfo and toggle:
            sslinfo.enabled = True
            session.commit()
            logger.info('%s - ssl communication for nodeid %s %s'%
                   (username, nodeid, 'has been enabled')
                   ) 
            result = {
                    'pass' : True,
                    'message' : 'node_id %s has been enabled' %
                            (nodeid)
                    }
        elif sslinfo and not toggle:
            sslinfo.enabled = False
            session.commit()
            logger.info('%s - ssl communication for nodeid %s %s'%
                            (username, nodeid, 'has been disabled')
                    ) 
            result = {
                    'pass' : True,
                    'message' : 'node_id %s has been disabled' %
                            (nodeid)
                     }
    else:
        logger.warn('%s - invalid nodeid %s' % (username, nodeid))
        result = {
                'pass' : False,
                'message' : 'node_id %s does not exist' % 
                        (nodeid)
                }
    return(result)


def get_node_stats(session, nodeid=None, hostname=None,
        displayname=None, computername=None,
        username='system_user'):
    """
        return a list of node_statistics in json
    """
    session = validate_session(session)
    node = None
    if nodeid:
        node = session.query(NodeInfo).\
            filter(NodeInfo.id == nodeid).first()
    elif hostname:
        node = session.query(NodeInfo).\
            filter(NodeInfo.host_name == hostname).first()
    elif displayname:
        node = session.query(NodeInfo).\
            filter(NodeInfo.display_name == displayname).first()
    elif computername:
        node = session.query(NodeInfo).\
            filter(NodeInfo.computer_name == computername).first()
    else:
        result = {
            'pass': False,
            'message': 'Incorrect arguments passed'
            }
    if node:
        update_node_stats(session, node.id, username)
        node_stats = session.query(NodeStats).\
                filter(NodeStats.node_id == node.id).first()
        if node_stats:
            result = {
                    "id" : int(node.id),
                    "host_name" : node.host_name,
                    "display_name" : node.display_name,
                    "computer_name" : node.computer_name,
                    "ip_address" : node.ip_address,
                    "reboots_pending" : int(node_stats.reboots_pending),
                    "agents_down" : int(node_stats.agents_down),
                    "agents_up" : int(node_stats.agents_up),
                    "patches_completed" : int(node_stats.patches_installed),
                    "patches_available" : int(node_stats.patches_available),
                    "patches_failed" : int(noed_stats.patches_failed),
                    "patches_pending" : int(node_stats.patches_pending)
                }
    return(result)



