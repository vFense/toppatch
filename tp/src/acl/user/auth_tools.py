#!/usr/bin/env python
import re
import logging, logging.config
from db.client import validate_session
from models.user_acl import *
from models.account import *
from models.node import *

from sqlalchemy import or_

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')

#def list_all_user_permission(session):

def verify_user(session, user_name=None, action=None, node_id=None,
        host_name=None, display_name=None, ip_address=None, tag_id=None,
        tag_name=None, user_id=None
        ):
    session = validate_session(session)
    global_query = session.query(GlobalUserAccess)
    node_query = session.query(NodeUserAccess)
    tag_query = session.query(NodeUserAccess)
    groups = None
    user = None
    node = None
    tag = None
    user_access = None
    user_for_node_exists = None
    user_for_tag_exists = None
    operation_call = ['install', 'uninstall', 'reboot', 'wol',
            'create_tag', 'remove_tag', 'create_snapshot',
            'remove_snap_shot', 'revert_snapshot']
    if host_name:
        node = session.query(NodeInfo).\
                filter(NodeInfo.host_name == host_name).first()
    elif display_name:
        node = session.query(NodeInfo).\
                filter(NodeInfo.host_name == display_name).first()
    elif ip_address:
        node = session.query(NodeInfo).\
                filter(NodeInfo.host_name == ip_address).first()
    elif node_id:
        node = session.query(NodeInfo).\
                filter(NodeInfo.id == node_id).first()
    if tag_name:
        tag = session.query(TagInfo).\
                filter(TagInfo.tag == tag_name).first()
    if tag_id:
        tag = session.query(TagInfo).\
                filter(TagInfo.id == tag_id).first()
    if user_name:
        user = session.query(User).\
                filter(User.username == user_name).first()
    if user_id:
        user = session.query(User).\
                filter(User.id == user_id).first()
    if user:
        groups = map(lambda gid: gid.group_id, session.query(UsersInAGroup).\
                filter(UsersInAGroup.user_id == user.id).all())
        if len(groups) >= 1:
             group_access = global_query.\
                    filter(GlobalUserAccess.group_id.in_(groups)).all()
        else:
            user_access = global_query.\
                    filter(GlobalUserAccess.user_id == user.id).first()
        elif user_access.is_admin and action in operation_call or\
                True in map(lambda gid: gid.is_admin, groups):
                logger.info('User %s is an admin' % (user.username))
                return True
            elif user_access.is_admin and not action in operation_call:
                logger.info('Invalid Operation %s' % (action))
                return False
            if node:
                user_for_node_exists = node_query.\
                        filter(NodeUserAccess.node_id == node.id).\
                        filter(_or(NodeUserAccess.user_access == user_access.id,
                            NodeUserAccess.group_id.in_(groups))).\
                        filter(NodeUserAccess.user_id == user.id).first()
            if tag:
                user_for_tag_exists = tag_query.\
                        filter(TagUserAccess.tag_id == tag.id).\
                        filter(TagUserAccess.user_access == user_access.id).\
                        filter(_or(TagUserAccess.user_access == user_access.id,\
                            TagUserAccess.group_id.in_(groups))).\
                        filter(TagUserAccess.user_id == user.id).first()
            if action in operation_call:
                if re.search(r'^create_tag$', action):
                    if user_access.is_global and user_access.allow_tag_creation\
                            and not user_access.is_admin:
                        logger.info('%s - %s has global permission for %s' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_tag_creation:
                            logger.info('%s - %s has %s permission on node  %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt has %s'%\
                                    (user.username, user.username, action)+
                                    'permission on node  %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_tag_creation:
                            logger.info('%s - %s has %s'%\
                                    (user.username, user.username, action)+
                                    'permission on this tag  %s' %\
                                        (tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt has %s'%\
                                    (user.username, user.username, action)+
                                    'permission on this tag  %s' %\
                                        (tag.tag)
                                    )
                            return False
                if re.search(r'^remove_tag$', action):
                    if user_access.is_global and user_access.allow_tag_removal:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_tag_removal:
                            logger.info('%s - %s has %s permission' %\
                                    (user.username, user.username, action)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s'+\
                                    'permission on %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_tag_removal:
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s'%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                if re.search(r'^install$', action):
                    if user_access.is_global and user_access.allow_install:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_install:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s'% \
                                    (user.username, user.username, action)+
                                    'permission on node %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_install:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                if re.search(r'^uninstall$', action):
                    if user_access.is_global and user_access.allow_uninstall:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_uninstall:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on node %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_uninstall:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                if re.search(r'^reboot$', action):
                    if user_access.is_global and user_access.allow_reboot:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_reboot:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on node %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_reboot:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                if re.search(r'^wol$', action):
                    if user_access.is_global and user_access.allow_wol:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_wol:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on node %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_wol:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                elif re.search(r'^create_snapshot$', action):
                    if user_access.is_global and user_access.allow_snapshot_creation:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_snapshot_creation:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '+\
                                    (user.username, user.username, action,
                                    'permission on node %s' %\
                                        node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_snapshot_creation:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                elif re.search(r'^remove_snapshot$', action):
                    if user_access.is_global and user_access.allow_snapshot_remove:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_snapshot_remove:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on node %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_snapshot_creation:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                elif re.search(r'^revert_snapshot$', action):
                    if user_access.is_global and user_access.allow_snapshot_revert:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_snapshot_revert:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%
                                    (user.username, user.username, action)+
                                    'permission on node %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_snapshot_revert:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                elif re.search('^revert_snapshot$', action):
                    if user_access.is_global and user_access.allow_snapshot_revert:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_snapshot_revert:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '+\
                                    'permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_snapshot_revert:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                elif re.search(r'^read_only$', action):
                    if user_access.is_global and user_access.view_only:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.view_only:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on node %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.view_only:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False
                elif re.search(r'^schedule$', action):
                    if user_access.is_global and user_access.allow_schedule:
                        logger.info('%s - %s has %s permission' %\
                                (user.username, user.username, action)
                                )
                        return True
                    elif user_for_node_exists:
                        if user_for_node_exists.allow_schedule:
                            logger.info('%s - %s has %s permission on node %s' %\
                                    (user.username, user.username, action,
                                        node.ip_address)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on node %s' %\
                                        (node.ip_address)
                                    )
                            return False
                    elif user_for_tag_exists:
                        if user_for_tag_exists.allow_schedule:
                            logger.info('%s - %s has %s permission on tag %s' %\
                                    (user.username, user.username, action,
                                        tag.tag)
                                    )
                            return True
                        else:
                            logger.info('%s - %s doesnt have %s '%\
                                    (user.username, user.username, action)+
                                    'permission on %s' %\
                                        (tag.tag)
                                    )
                            return False

                else:
                    logger.info('1st else Operation %s is not valid' % (action))
                    return False
            else:
                logger.info('2nd else Operation %s is not valid' % (action))
                return False
        else:
            logger.info('%s - %s doesnt have Global Permissions set' %\
                    (user.username, user.username)
                    )
            return False
    else:
        logger.info('%s - %s doesnt exist' %\
                (user_name, user_name)
                )
        return False


    def group_acl_exists(self, node=None, tag=None):
        if node:
            self.user_for_node_exists = node_query.\
                    filter(NodeUserAccess.node_id == node.id).\
                    filter(_or(NodeUserAccess.user_access == user_access.id,
                        NodeUserAccess.group_id.in_(groups))).\
                    filter(NodeUserAccess.user_id == user.id).first()
        if tag:
            self.user_for_tag_exists = tag_query.\
                    filter(TagUserAccess.tag_id == tag.id).\
                    filter(TagUserAccess.user_access == user_access.id).\
                    filter(_or(TagUserAccess.user_access == user_access.id,\
                        TagUserAccess.group_id.in_(groups))).\
                    filter(TagUserAccess.user_id == user.id).first()


    def has_permission(self, user=None, groups=None,
            user_access=None, group_access=None, node=None,
            tag=None, acl_key=None):
        if user_access:
            user_hash = user_access.__dict__
            if True in user_hash['is_global'] and True in user_hash[acl_key] \
                    and False in user_hash['is_admin']:
                logger.info('%s - %s has global permission for %s' %\
                        (user.username, user.username, action)
                        )
                return True
            elif self.user_for_node_exists:
                if True in user_hash[acl_key] and \
                        False in user_hash['is_admin']:
                    logger.info('%s - %s has %s permission on node  %s' %\
                            (user.username, user.username, action, node.ip_address)
                            )
                    return True
                else:
                    logger.info('%s - %s doesnt has %s'%\
                            (user.username, user.username, action)+
                            'permission on node  %s' %\
                            (node.ip_address)
                            )
                    return False
            elif self.user_for_tag_exists:
                if True in user_hash[acl_key] and \
                        False in user_hash['is_admin']:
                    logger.info('%s - %s has %s'%\
                            (user.username, user.username, action)+
                            'permission on this tag  %s' %\
                            (tag.tag)
                            )
                    return True
                else:
                    logger.info('%s - %s doesnt has %s'%\
                            (user.username, user.username, action)+
                            'permission on this tag  %s' %\
                            (tag.tag)
                        )
                    return False

        elif group_access:
            if True in map(lambda gid: gid.is_global, group_access) and \
                    True in map(lambda gid: gid.allow_tag_creation, group_access) \
                    and not user_access.is_admin:
                logger.info('%s - %s has global permission for %s' %\
                        (user.username, user.username, action)
                        )
                return True
        elif user_for_node_exists:
            if user_for_node_exists.allow_tag_creation:
                logger.info('%s - %s has %s permission on node  %s' %\
                        (user.username, user.username, action, node.ip_address)
                        )
                return True
            else:
                logger.info('%s - %s doesnt has %s'%\
                        (user.username, user.username, action)+
                        'permission on node  %s' %\
                        (node.ip_address)
                        )
                return False
        elif user_for_tag_exists:
            if user_for_tag_exists.allow_tag_creation:
                logger.info('%s - %s has %s'%\
                        (user.username, user.username, action)+
                        'permission on this tag  %s' %\
                        (tag.tag)
                        )
                return True
            else:
                logger.info('%s - %s doesnt has %s'%\
                        (user.username, user.username, action)+
                        'permission on this tag  %s' %\
                        (tag.tag)
                        )
                return False


