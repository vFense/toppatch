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

class VerifyUser():
    def __init__(self, session, user_name=None, action=None, node_id=None,
        host_name=None, display_name=None, ip_address=None, tag_id=None,
        tag_name=None, user_id=None
        ):
        self.session = validate_session(session)
        self.global_query = self.session.query(GlobalUserAccess)
        self.node_query = self.session.query(NodeUserAccess)
        self.tag_query = self.session.query(TagUserAccess)
        self.node_id = node_id
        self.host_name = host_name
        self.display_name = display_name
        self.ip_address = ip_address
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.user_id = user_id
        self.user_name = user_name
        self.action = action
        self.groups = None
        self.user = None
        self.node = None
        self.tag = None
        self.user_access = None
        self.group_access = None
        self.user_for_node_exists = None
        self.user_for_tag_exists = None
        self.global_user_name = None
        self.user_auth = []
        self.group_auth = []
        self.operation_call = ['allow_install', 'allow_uninstall',
                'allow_reboot', 'allow_wol', 'allow_tag_creation', 
                'allow_tag_removal', 'allow_snapshot_creation',
                'allow_snapshot_removal', 'allow_snapshot_revert'
                ]

    def run(self):
        self._set_sql_objects()
        if self.user:
            self.groups = map(lambda gid: gid.group_id,
                    self.session.query(UsersInAGroup).\
                    filter(UsersInAGroup.user_id == self.user.id).\
                    all())
            if len(self.groups) >= 1:
                self.group_access = self.global_query.\
                        filter(GlobalUserAccess.group_id.in_(self.groups)).\
                        all()
                if len(self.group_access) >=1:
                    if True in map(lambda gid: gid.is_admin, self.group_access)\
                            and self.action in self.operation_call:
                        logger.info('User %s is an admin group' % \
                                (self.user.username))
                        return True
            self.user_access = self.global_query.\
                    filter(GlobalUserAccess.user_id == self.user.id).\
                    first()
            if self.user_access:
                if self.user_access.is_admin and \
                        self.action in self.operation_call:
                    logger.info('User %s is an admin' %\
                            (self.user.username))
                    return True
                elif self.user_access.is_admin and not self.action \
                        in self.operation_call:
                    logger.info('Invalid Operation %s' % (self.action))
                    return False
            if self.action in self.operation_call:
                self._get_acls()
                permissions = self.has_permission()
                return(permissions)
            else:
                logger.info('1st else Operation %s is not valid' % (self.action))
                return False
            if not self.user_access or self.group_access:
                logger.info('%s - %s doesnt have Global Permissions set' %\
                        (self.user.username, self.user.username)
                        )
                return False
        if not user:
            logger.info('%s - Username or ID %s doesnt exist' %\
                    (self.global_user_name, self.global_user_name)
                    )
            return False

    def _set_sql_objects(self):

        if selfhost_name:
            self.node = self.session.query(NodeInfo).\
                    filter(NodeInfo.host_name == self.host_name).first()
        elif self.display_name:
            self.node = self.session.query(NodeInfo).\
                    filter(NodeInfo.host_name == self.display_name).first()
        elif self.ip_address:
            self.node = self.session.query(NodeInfo).\
                    filter(NodeInfo.host_name == self.ip_address).first()
        elif self.node_id:
            self.node = self.session.query(NodeInfo).\
                    filter(NodeInfo.id == self.node_id).first()
        if self.tag_name:
            self.tag = self.session.query(TagInfo).\
                    filter(TagInfo.tag == self.tag_name).first()
        if self.tag_id:
            self.tag = self.session.query(TagInfo).\
                    filter(TagInfo.id == self.tag_id).first()
        if self.user_name:
            self.user = self.session.query(User).\
                    filter(User.username == self.user_name).first()
            self.global_user_name = self.user_name
        if self.user_id:
            self.user = self.session.query(User).\
                    filter(User.id == self.user_id).first()
            self.global_user_name = self.user_id

    def _get_acls(self):
        self.user_for_node_exists = None
        self.group_for_node_exists = None
        self.user_for_tag_exists = None
        self.user_for_nodes_if_tag_doesnt_exists = None
        self.nodes_in_a_tag = None
        self.group_for_tag_exists = None
        self.tag_length_of_nodes = 0
        self.tag_length_of_nodes_that_have_acls = 0
        self.user_for_nodes_if_tag_exists_dict = None
        self.group_for_nodes_if_tag_exists_dict = None
        if self.node and self.user_access:
            self.user_for_node_exists = self.node_query.\
                    filter(NodeUserAccess.node_id == self.node.id).\
                    filter(NodeUserAccess.user_id == self.user.id).first()
            self.user_node_dict = self.user_for_node_exists.__dict__
        if self.node and self.group_access:
            self.group_for_node_exists = self.node_query.\
                    filter(NodeUserAccess.group_id.in_(self.groups)).all()
            self.group_node_dict = map(lambda gid: gid.__dict__, 
                    self.group_for_node_exists)
        if self.tag and self.user_access:
            self.user_for_tag_exists = self.tag_query.\
                    filter(TagUserAccess.tag_id == self.tag.id).\
                    filter(TagUserAccess.user_id == self.user.id).first()
            if self.user_for_tag_exists:
                self.user_tag_dict = self.user_for_tag_exists.__dict__
            else:
                self.nodes_in_a_tag = map(lambda nodes: nodes.node_id, \
                        self.session.query(TagsPerNode).\
                        filter(TagsPerNode.tag_id == self.tag.id).all())
                if len(self.nodes_in_a_tag) >=1:
                    self.tag_length_of_nodes = len(self.nodes_in_a_tag)
                    self.user_for_nodes_if_tag_exists = self.node_query.\
                            filter(NodeUserAccess.node_id.\
                            in_(self.nodes_in_a_tag)).\
                            filter(NodeUserAccess.user_id == self.user.id).all()
                    self.tag_length_of_nodes_that_have_acls = \
                            len(self.user_for_nodes_if_tag_exists)
                    if self.tag_length_of_nodes_that_have_acls >=1:
                        self.user_for_nodes_if_tag_exists_dict = \
                                map(lambda nodes: nodes.__dict__,\
                                self.user_for_nodes_if_tag_exists)
        if self.tag and self.group_access:
            self.group_for_tag_exists = self.tag_query.\
                    filter(TagUserAccess.group_id.in_(self.groups)).\
                    filter(TagUserAccess.tag_id == self.tag.id).all()
            if len(self.group_for_tag_exists) >=1:
                self.group_tag_dict = map(lambda gid: gid.__dict__, 
                        self.group_for_tag_exists)
            else:
                self.nodes_in_a_tag = map(lambda nodes: nodes.node_id, \
                        self.session.query(TagsPerNode).\
                        filter(TagsPerNode.tag_id == self.tag.id).all())
                if len(self.nodes_in_a_tag) >=1:
                    self.tag_length_of_nodes = len(self.nodes_in_a_tag)
                    self.group_for_nodes_if_tag_exists = self.node_query.\
                            filter(NodeUserAccess.node_id.\
                            in_(self.nodes_in_a_tag)).\
                            filter(NodeUserAccess.group_id.in_(self.groups).all()
                    self.tag_length_of_nodes_that_have_acls = \
                            len(self.group_for_nodes_if_tag_exists)
                    if len(self.group_for_nodes_if_tag_exists) >=1:
                        self.group_for_nodes_if_tag_exists_dict = \
                                map(lambda nodes: nodes.__dict__,\
                                self.group_for_nodes_if_tag_exists)

    def _has_permission(self):
        acl_key = self.action

        #Check User Settings
        if self.user_access:
            user_hash = self.user_access.__dict__
            #Check Global User Settings
            if user_hash[acl_key] and user_access.is_global:
                logger.info('%s - %s has global permission for %s' %\
                        (self.user.username, self.user.username, acl_key)
                        )
                #return True
                self.user_auth.append([self.user.username, 'User', 'Global',
                    acl_key, True])
            #Check Node User Settings
            if self.user_for_node_exists:
                if user_node_hash[acl_key] and \
                        False in user_access.is_admin:
                    logger.info('%s - %s has %s permission on node  %s' %\
                            (self.user.username, self.user.username,
                                acl_key, self.node.ip_address)
                            )
                    #return True
                    self.user_auth.append([self.user.username, 'User', 'Node',
                        'Node', acl_key, True])
                else:
                    logger.info('%s - %s doesnt has %s'%\
                            (self.user.username, self.user.username, acl_key)+
                            'permission on node  %s' %\
                            (self.node.ip_address)
                            )
                    #return False
                    self.user_auth.append([self.user.username, 'User', 'Node',
                        'Node', acl_key, False])
            #Check Tag User Settings
            if self.user_for_tag_exists:
                if self.user_tag_dict[acl_key] and \
                        False in user_access.is_admin:
                    logger.info('%s - %s has %s'%\
                            (self.user.username, self.user.username, acl_key)+
                            'permission on this tag  %s' %\
                            (self.tag.tag)
                            )
                    #return True
                    self.user_auth.append([self.user.username, 'User', 'Tag',
                        acl_key, True])
                else:
                    logger.info('%s - %s doesnt has %s'%\
                            (self.user.username, self.user.username, acl_key)+
                            'permission on this tag  %s' %\
                            (self.tag.tag)
                        )
                    #return False
                    self.user_auth.append([self.user.username, 'User', 'Tag',
                        acl_key, False])
            if self.user_for_nodes_if_tag_doesnt_exists:
        #Check Tag Group Settings
        if self.group_access:
            group_dict = map(lambda gid: gid.__dict__, self.group_access)
            #Check Global Group Settings
            if True in map(lambda gid: gid['is_global'], group_dict) and \
                    acl_key in map(lambda gid: gid[acl_key], group_dict):
                logger.info('%s - %s has global permission for %s' %\
                        (self.user.username, self.user.username, acl_key)
                        )
                return True
            #Check Node Group Settings
            elif self.group_for_node_exists:
                if True in map(lambda gid: gid[acl_key], group_node_dict):
                    logger.info('%s - %s has %s permission on node  %s' %\
                            (self.user.username, self.user.username,
                                acl_key, self.node.ip_address)
                            )
                    return True
                else:
                    logger.info('%s - %s doesnt has %s'%\
                            (self.user.username, self.user.username, acl_key)+
                            'permission on node  %s' %\
                            (self.node.ip_address)
                            )
                    return False
            #Check Tag Group Settings
            elif self.group_for_tag_exists:
                if True in map(lambda gid: gid[acl_key], group_tag_dict):
                    logger.info('%s - %s has %s'%\
                            (self.user.username, self.user.username, acl_key)+
                            'permission on this tag  %s' %\
                            (self.tag.tag)
                            )
                    return True
                else:
                    logger.info('%s - %s doesnt has %s'%\
                            (self.user.username, self.user.username, acl_key)+
                            'permission on this tag  %s' %\
                            (self.tag.tag)
                            )
                    return False
        else:
            return False
