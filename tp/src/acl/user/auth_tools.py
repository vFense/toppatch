#!/usr/bin/env python
import re
import logging, logging.config
from db.client import validate_session
from models.user_acl import *
from models.account import *
from models.node import *
from models.tagging import *

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
        self.global_user_query = self.session.query(GlobalUserAccess)
        self.global_group_query = self.session.query(GlobalGroupAccess)
        self.node_user_query = self.session.query(NodeUserAccess)
        self.node_group_query = self.session.query(NodeGroupAccess)
        self.tag_user_query = self.session.query(TagUserAccess)
        self.tag_group_query = self.session.query(TagGroupAccess)
        self.node_id = node_id
        self.host_name = host_name
        self.display_name = display_name
        self.ip_address = ip_address
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.tag_names = []
        self.user_id = user_id
        self.user_name = user_name
        self.action = action
        self.groups = []
        self.user = None
        self.node = None
        self.nodes = []
        self.tag = None
        self.tags = []
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
            if self.node:
                if self.session.query(TagsPerNode).\
                        filter(TagsPerNode.node_id == self.node.id).first():
                    #Create a list of tag ids
                    self.tags = map(lambda tid: tid.tag_id, \
                            self.session.query(TagsPerNode).\
                            filter(TagsPerNode.node_id == self.node.id).all())
                    #Create a list of tag names
                    self.tag_names = map(lambda tagid: tagid.tag, \
                            self.session.query(TagInfo).\
                            filter(TagInfo.id.in_(self.tags)).all())
            #Create a list of group id's that the user belongs too
            self.groups = map(lambda gid: gid.group_id,
                    self.session.query(UsersInAGroup).\
                    filter(UsersInAGroup.user_id == self.user.id).\
                    all())
            if len(self.groups) >= 1:
                #Verify if any of the groups actually have an ACL Globally
                self.group_access = self.global_group_query.\
                        filter(GlobalGroupAccess.group_id.in_(self.groups)).\
                        all()
                if len(self.group_access) >=1:
                    #If any of those groups that the user is part of has
                    #is_admin set to True, then the user has admin
                    #privileges.
                    if True in map(lambda gid: gid.is_admin, self.group_access)\
                            and self.action in self.operation_call:
                        logger.info('User %s is an admin group' % \
                                (self.user.username))
                        return True
            #Verify if any if the user actually haves an ACL Globally
            self.user_access = self.global_user_query.\
                    filter(GlobalUserAccess.user_id == self.user.id).\
                    first()
            if self.user_access:
                #Verify If the user has the is_admin set to True, 
                #then the user has admin privileges.
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
                #This is where all the magic happens
                self._get_acls_if_exist()
                permissions = self._has_permission()
                return(permissions)
            else:
                logger.info('1st else Operation %s is not valid' % (self.action))
                return False
            if not self.user_access or self.group_access:
                logger.info('%s - %s doesnt have Global Permissions set' %\
                        (self.user.username, self.user.username)
                        )
                return False
        if not self.user:
            logger.info('%s - Username or ID %s doesnt exist' %\
                    (self.global_user_name, self.global_user_name)
                    )
            return False

    def _set_sql_objects(self):
        """
            This is where we set the global sqllalchemy objects on
            the arguments that were passed to the init methood
        """
        if self.host_name:
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

    def _get_acls_if_exist(self):
        self.user_for_node_exists = None
        self.group_for_node_exists = None
        self.user_for_tag_exists = None
        self.user_for_nodes_if_tag_exists = None
        self.group_for_nodes_if_tag_exists = None
        self.group_for_tag_exists = None
        self.tags_for_node_exists = None
        self.tags_for_group_exists = None
        self.nodes_in_a_tag = None
        self.tag_length_of_nodes = 0
        self.tag_length_of_nodes_that_have_acls = 0
        self.group_node_dict = None
        self.user_node_dict = None
        self.tag_node_dict = None
        self.tag_group_dict = None
        self.user_tag_dict = None
        self.group_tag_dict = None
        self.user_for_nodes_if_tag_exists_dict = None
        self.group_for_nodes_if_tag_exists_dict = None
        #SQLAlchemy Object if there is an ACL in the NodeUserAccess table
        if self.node:
            self.user_for_node_exists = self.node_user_query.\
                    filter(NodeUserAccess.node_id == self.node.id).\
                    filter(NodeUserAccess.user_id == self.user.id).first()
            if self.user_for_node_exists:
                self.user_node_dict = self.user_for_node_exists.__dict__
        #SQLAlchemy Object, if there is an ACL in the TagUserAccess table
        #This is ran if the tag arguement was not passed and we want to verify
        #if the node_id that was passed is part of any tags that may have an
        #ACL.
        if self.node and len(self.tags) >=1:
            self.tags_for_node_exists = self.tag_user_query.\
                    filter(TagUserAccess.tag_id.in_(self.tags)).\
                    filter(TagUserAccess.user_id == self.user.id).all()
            if len(self.tags_for_node_exists) >=1:
                self.tag_node_dict = map(lambda tags: tags.__dict__,\
                        self.tags_for_node_exists)
        #SQLAlchemy Object, if there is an ACL in the NodeGroupAccess table
        if self.node and len(self.groups) >=1:
            self.group_for_node_exists = self.node_group_query.\
                    filter(NodeGroupAccess.group_id.in_(self.groups)).all()
            self.group_node_dict = map(lambda gid: gid.__dict__, 
                    self.group_for_node_exists)
        #SQLAlchemy Object, if there is an ACL in the TagGroupAccess table
        #This is ran if the tag arguement was not passed and we want to verify
        #if the node_id that was passed is part of any tags that may have an
        #ACL.
        if self.node and len(self.tags) >=1 and len(self.groups) >=1:
            self.tags_for_group_exists = self.tag_group_query.\
                    filter(TagGroupAccess.tag_id.in_(self.tags)).\
                    filter(TagGroupAccess.group_id.in_(self.groups)).all()
            if len(self.tags_for_group_exists) >=1:
                self.tag_group_dict = map(lambda tags: tag.__dict__,\
                        self.tag_for_group_exists)
        #SQLAlchemy Object, if there is an ACL in the TagUserAccess table
        #This is ran if a tag arguement was passed. This will also check
        #if the nodes in the tag that was passed actually have an acl to it.
        if self.tag:
            self.user_for_tag_exists = self.tag_user_query.\
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
                    self.user_for_nodes_if_tag_exists = self.node_user_query.\
                            filter(NodeUserAccess.node_id.\
                            in_(self.nodes_in_a_tag)).\
                            filter(NodeUserAccess.user_id == self.user.id).all()
                    self.tag_length_of_nodes_that_have_acls = \
                            len(self.user_for_nodes_if_tag_exists)
                    if self.tag_length_of_nodes_that_have_acls >=1:
                        self.user_for_nodes_if_tag_exists_dict = \
                                map(lambda nodes: nodes.__dict__,\
                                self.user_for_nodes_if_tag_exists)
        #SQLAlchemy Object, if there is an ACL in the TagGroupAccess table
        #This is ran if the tag arguement was not passed and we want to verify
        #if the node_id that was passed is part of any tags that may have an
        #ACL.
        if self.tag and len(self.groups) >=1:
            self.group_for_tag_exists = self.tag_group_query.\
                    filter(TagGroupAccess.group_id.in_(self.groups)).\
                    filter(TagGroupAccess.tag_id == self.tag.id).all()
            if len(self.group_for_tag_exists) >=1:
                self.group_tag_dict = map(lambda gid: gid.__dict__, 
                        self.group_for_tag_exists)
            else:
                self.nodes_in_a_tag = map(lambda nodes: nodes.node_id, \
                        self.session.query(TagsPerNode).\
                        filter(TagsPerNode.tag_id == self.tag.id).all())
                if len(self.nodes_in_a_tag) >=1:
                    self.tag_length_of_nodes = len(self.nodes_in_a_tag)
                    self.group_for_nodes_if_tag_exists = self.node_user_query.\
                            filter(NodeGroupAccess.node_id.\
                            in_(self.nodes_in_a_tag)).\
                            filter(NodeGroupAccess.group_id.in_(self.groups)).all()
                    self.tag_length_of_nodes_that_have_acls = \
                            len(self.group_for_nodes_if_tag_exists)
                    if len(self.group_for_nodes_if_tag_exists) >=1:
                        self.group_for_nodes_if_tag_exists_dict = \
                                map(lambda nodes: nodes.__dict__,\
                                self.group_for_nodes_if_tag_exists)

        print 'hash of group ', self.group_node_dict
        print 'hash of node ', self.user_node_dict
        print 'hash of tag node', self.tag_node_dict
        print 'hash of tag group', self.tag_group_dict
        print 'hash of user tag ', self.user_tag_dict
        print 'hash of group tag ', self.group_tag_dict
        print 'hash of user for nodes if tag exists ', self.user_for_nodes_if_tag_exists_dict
        print 'hash of groups for nodes if tag exists ', self.group_for_nodes_if_tag_exists_dict

    def _has_permission(self):
        acl_key = self.action

        #Check User Settings
        if self.user_access:
            user_hash = self.user_access.__dict__
            if user_hash[acl_key] and self.user_access.is_global:
                allowed = True
            else:
                allowed = False
            self.user_auth.append(self._return_json(
                self.user.username, 'Node',
                len(self.tags), self.tag_length_of_nodes_that_have_acls,
                ','.join(self.tag_names), ','.join(self.groups),
                acl_key, allowed)
                )
            #Check Node User Settings
        if self.user_for_node_exists:
            if self.user_node_dict[acl_key]:
                allowed = True
            else:
                allowed = False
            self.user_auth.append(self._return_json(
                self.user.username, 'Node',
                len(self.tags), self.tag_length_of_nodes_that_have_acls,
                ','.join(self.tag_names), ','.join(self.groups),
                acl_key, allowed)
                )
            #Check Tag User Settings
        if self.user_for_tag_exists:
            if self.user_tag_dict[acl_key]:
                allowed = True
            else:
                allowed = False
            self.user_auth.append(self._return_json(
                self.user.username, 'Node',
                len(self.tags), self.tag_length_of_nodes_that_have_acls,
                ','.join(self.tag_names), ','.join(self.groups),
                acl_key, allowed)
                )
        if self.user_for_nodes_if_tag_exists:
            if True in map(lambda uid: uid[acl_key],\
                    self.user_for_nodes_if_tag_exists_dict):
                allowed = True
            else:
                allowed = False
            self.user_auth.append(self._return_json(
                self.user.username, 'Node',
                len(self.tags), self.tag_length_of_nodes_that_have_acls,
                ','.join(self.tag_names), ','.join(self.groups),
                acl_key, allowed)
                )
        if self.tags_for_node_exists:
            if True in map(lambda uid: uid[acl_key],\
                    self.tag_node_dict):
                allowed = True
            else:
                allowed = False
            self.user_auth.append(self._return_json(
                self.user.username, 'Node',
                len(self.tags), self.tag_length_of_nodes_that_have_acls,
                ','.join(self.tag_names), ','.join(self.groups),
                acl_key, allowed)
                )

        #Check Tag Group Settings
        if len(self.groups) >=1:
            if self.group_access:
                group_dict = map(lambda gid: gid.__dict__, self.group_access)
                #Check Global Group Settings
                if True in map(lambda gid: gid['is_global'], group_dict) and \
                        acl_key in map(lambda gid: gid[acl_key], group_dict):
                    allowed = True
                else:
                    allowed = False
                self.user_auth.append(self._return_json(
                    self.user.username, 'Group',
                    len(self.tags), self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.groups),
                    acl_key, allowed)
                    )
            #Check Node Group Settings
            if self.group_for_node_exists:
                if True in map(lambda gid: gid[acl_key], self.group_node_dict):
                    allowed = True
                else:
                    allowed = False
                self.user_auth.append(self._return_json(
                    self.user.username, 'Node',
                    len(self.tags), self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.groups),
                    acl_key, allowed)
                    )
            #Check Tag Group Settings
            if self.group_for_tag_exists:
                if True in map(lambda gid: gid[acl_key], self.group_tag_dict):
                    allowed = True
                else:
                    allowed = False
                self.user_auth.append(self._return_json(
                    self.user.username, 'Tag',
                    len(self.tags), self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.groups),
                    acl_key, allowed)
                    )
            if self.group_for_nodes_if_tag_exists:
                if True in map(lambda uid: uid[acl_key],\
                        self.group_for_nodes_if_tag_exists_dict):
                    allowed = True
                else:
                    allowed = False
                self.user_auth.append(self._return_json(
                    self.user.username, 'Tag',
                    len(self.tags), self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.groups),
                    acl_key, allowed)
                    )
            if self.tag_for_groups_exists:
                if True in map(lambda uid: uid[acl_key],\
                        self.tag_for_group_exists_dict):
                    allowed = True
                else:
                    allowed = False
                self.user_auth.append(self._return_json(
                    self.user.username, 'Tag',
                    len(self.tags), self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.groups),
                    acl_key, allowed)
                    )

        print self.user_auth
        print self.group_auth
    def _return_json(self, username, vtype, nodes_in_tag, nodes_in_tag_acl,
            tagnames, groups, action, allowed):
        return({
            'user': username,
            'verification_type': vtype,
            'nodes_in_tag': nodes_in_tag,
            'nodes_in_tag_that_have_acl': nodes_in_tag_acl,
            'tag_names': tagnames,
            'groups': groups,
            'acl_action': action,
            'action_allowed': allowed
            })
        #else:
            #return False
            #return False
