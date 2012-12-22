#!/usr/bin/env python

import logging, logging.config
from db.update_table import *
from db.client import validate_session
from utils.common import *
from models.node import *

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
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


