#!/usr/bin/env python
import re
import logging, logging.config
from db.client import validate_session
from models.user_acl import *
from models.account import *
from models.node import *
from models.tagging import *

from sqlalchemy import or_

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

#def list_all_user_permission(session):

class VerifyUser():
    def __init__(self, session, user_name=None, action='allow_read', node_id=None,
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
        self.group_names = []
        self.user = None
        self.node = None
        self.nodes = []
        self.tag = None
        self.tags = []
        self.acls = []
        self.global_acls = None
        self.node_or_tag_acls = None
        self.user_access = None
        self.group_access = None
        self.user_for_node_exists = None
        self.user_for_tag_exists = None
        self.global_user_name = None
        self.operation_call = [
                'allow_install', 'allow_uninstall', 'allow_read',
                'allow_reboot', 'allow_wol', 'allow_tag_creation', 
                'allow_tag_removal', 'allow_snapshot_creation',
                'allow_snapshot_removal', 'allow_snapshot_revert'
                ]

    def verify(self):
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
            elif self.tag:
                self.tags = [self.tag.id]
                self.tag_names = [self.tag.tag]
            #Create a list of group id's that the user belongs too
            self.groups = map(lambda gid: gid.group_id,
                    self.session.query(UsersInAGroup).\
                    filter(UsersInAGroup.user_id == self.user.id).\
                    all())
            if len(self.groups) >= 1:
                self.group_names = map(lambda gid: gid.groupname, \
                            self.session.query(Group).\
                            filter(Group.id.in_(self.groups)).all())
                self.group_access = self.global_group_query.\
                        filter(GlobalGroupAccess.group_id.in_(self.groups)).\
                        all()
            self.user_access = self.global_user_query.\
                    filter(GlobalUserAccess.user_id == self.user.id).\
                    first()
            if self.action in self.operation_call:
                #This is where all the magic happens
                if self.user_access or self.group_access:
                    self.global_acls = self._verify_global_user_or_group_has_acl()
                if self.node or self.tag:
                    self._get_acls_if_exist()
                    self.node_or_tag_acls = self._verify_node_or_tag_has_acl()
                self.total_acls = {
                        'global_acls': self.global_acls,
                        'node_or_tag_acls': self.node_or_tag_acls
                        }
                if len(self.global_acls) >=1 or\
                        len(self.node_or_tag_acls) >=1:
                    return(self.total_acls)
                else:
                    print self.acls
                    return({
                        'pass': False,
                        'message': 'Operation %s denied FOR %s' % \
                                (self.action, self.user.username)
                        })
            else:
                return({
                    'pass': False,
                    'message': 'Operation %s is not valid' % (self.action),
                    })
        else:
            return({
                'pass': False,
                'message': 'Username or ID %s doesnt exist' % \
                        (self.global_user_name)
                })

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
        self.node_in_a_group_acl = 0
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
        if self.node and len(self.tags) >=1 and not self.tag:
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
            if self.group_for_node_exists:
                self.group_node_dict = map(lambda gid: gid.__dict__, 
                        self.group_for_node_exists)
                self.node_in_a_group_acl = len(self.group_for_node_exists)
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
                        self.tags_for_group_exists)
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
                    #Check if user has an ACL on the node if the Tag 
                    #that was passed does not have an ACL.
                    if self.user_for_nodes_if_tag_exists:
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
        if self.tag and len(self.groups) >=1 and len(self.tags) ==0:
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
                    #Check if the group the user is under has an ACL if the
                    #Tag that was passed does not have an ACL.
                    if self.group_for_nodes_if_tag_exists:
                        self.tag_length_of_nodes_that_have_acls = \
                                len(self.group_for_nodes_if_tag_exists)
                        if self.tag_length_of_nodes_that_have_acls >=1:
                            self.group_for_nodes_if_tag_exists_dict = \
                                    map(lambda nodes: nodes.__dict__,\
                                    self.group_for_nodes_if_tag_exists)


    def _verify_global_user_or_group_has_acl(self):
        acl_key = self.action
        acl = []
        #Check User Settings
        if self.user_access:
            user_hash = self.user_access.__dict__
            if not self.user_access.is_admin:
                if user_hash[acl_key] and self.user_access.is_global:
                    allowed = True
                    message = 'User %s has %s globally' %\
                            (self.user.username, acl_key)
                    acl.append(self._return_global_json(
                        self.user.username, 'Global User ACL', 
                        ','.join(self.group_names),
                        acl_key, allowed, message)
                        )

            elif self.user_access.is_admin:
                if self.user_access.is_global:
                    allowed = True
                    message = 'User %s is a global admin' %\
                            (self.user.username)
                    acl.append(self._return_global_json(
                        self.user.username, 'Global User ACL', 
                        ','.join(self.group_names),
                        acl_key, allowed, message)
                        )

            elif self.user_access.deny_all:
                if self.user_access.is_global:
                    allowed = False
                    message = 'User %s has the deny_all rule set' %\
                            (self.user.username)
                    acl.append(self._return_global_json(
                        self.user.username, 'Global User ACL', 
                        ','.join(self.group_names),
                        acl_key, allowed, message)
                        )

        if self.group_access:
            #Check Global Group Settings
            group_dict = map(lambda gid: gid.__dict__, self.group_access)
            if True in map(lambda gid: gid['is_global'], group_dict) and \
                    True in map(lambda gid: gid[acl_key], group_dict)\
                    and False in map(lambda gid: gid['is_admin'], group_dict):
                allowed = True
                message = 'User %s has %s globally through a Group ACL' %\
                        (self.user.username, acl_key)
                acl.append(self._return_global_json(
                    self.user.username, 'Global Group ACL',
                    ','.join(self.group_names),
                    acl_key, allowed, message)
                    )

            elif True in map(lambda gid: gid['is_admin'], group_dict)\
                    and True in map(lambda gid: gid['is_global'], group_dict):
                allowed = True
                message = 'User %s is a global admin in a Group ACL' %\
                        (self.user.username)
                acl.append(self._return_global_json(
                    self.user.username, 'Global Group ACL',
                    ','.join(self.group_names),
                    acl_key, allowed, message)
                    )

            elif True in map(lambda gid: gid['deny_all'], group_dict)\
                    and True in map(lambda gid: gid['is_global'], group_dict):
                allowed = False
                message = 'User %s has deny all access in a Group ACL' %\
                        (self.user.username)
                acl.append(self._return_global_json(
                    self.user.username, 'Global Group ACL',
                    ','.join(self.group_names),
                    acl_key, allowed, message)
                    )

        return(acl)


    def _verify_node_or_tag_has_acl(self):
        acl_key = self.action
        acl = []

        #Check Node User Settings
        if self.user_for_node_exists:
            if self.user_node_dict[acl_key]:
                allowed = True
                message = 'ACL for %s exists for node %s' %\
                        (self.user.username, self.node.ip_address)

                acl.append(self._return_node_or_tag_json(
                    self.user.username, 'Node User ACL',len(self.tags), 
                    self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.group_names),
                    acl_key, allowed, message)
                    )

            #Check Tag User Settings
        if self.user_for_tag_exists:
            if self.user_tag_dict[acl_key]:
                allowed = True
                message = 'ACL for %s exists for tag %s' %\
                        (self.user.username, self.tag.tag)
                acl.append(self._return_node_or_tag_json(
                    self.user.username, 'Tag User ACL', len(self.tags),
                    self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.group_names),
                    acl_key, allowed, message)
                    )

        if self.user_for_nodes_if_tag_exists:
            if True in map(lambda uid: uid[acl_key],\
                    self.user_for_nodes_if_tag_exists_dict) and \
                    self.tag_length_of_nodes_that_have_acls == \
                    len(self.tag_length_of_nodes):
                allowed = True
                message = 'ACL for %s %s %s %s %s'%\
                        (self.user.username, self.tag.tag,
                                'exists for all the nodes in this tag.',
                                'This Tag should have an ACL instead',
                                'of the nodes.')
                acl.append(self._return_node_or_tag_json(
                    self.user.username, 'Node User ACL', len(self.tags),
                    self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.group_names),
                    acl_key, allowed, message)
                    )

        if self.tags_for_node_exists:
            if True in map(lambda uid: uid[acl_key],\
                    self.tag_node_dict):
                allowed = True
                message = 'ACL for %s %s %s'%\
                        (self.user.username,
                                'exists for a Tag that is associated',
                                'with this node')
                acl.append(self._return_node_or_tag_json(
                    self.user.username, 'Node Tag ACL', len(self.tags),
                    self.tag_length_of_nodes_that_have_acls,
                    ','.join(self.tag_names), ','.join(self.group_names),
                    acl_key, allowed, message)
                    )

        #Check Tag Group Settings
        if len(self.groups) >=1:
            #Check Node Group Settings
            if self.group_for_node_exists:
                if True in map(lambda gid: gid[acl_key], self.group_node_dict):
                    allowed = True
                    message = 'Group ACL for %s exists for node %s' %\
                            (self.user.username, self.node.ip_address)
                    acl.append(self._return_node_or_tag_json(
                        self.user.username, 'Node Group ACL', len(self.tags),
                        self.tag_length_of_nodes_that_have_acls,
                        ','.join(self.tag_names), ','.join(self.group_names),
                        acl_key, allowed, message)
                        )

            #Check Tag Group Settings
            if self.group_for_tag_exists:
                if True in map(lambda gid: gid[acl_key], self.group_tag_dict):
                    allowed = True
                    message = 'Group ACL for %s exists for tag %s' %\
                            (self.user.username, self.tag.tag)
                    acl.append(self._return_node_or_tag_json(
                        self.user.username, 'Tag Group ACL', len(self.tags),
                        self.tag_length_of_nodes_that_have_acls,
                        ','.join(self.tag_names), ','.join(self.group_names),
                        acl_key, allowed, message)
                        )

            if self.group_for_nodes_if_tag_exists:
                if True in map(lambda uid: uid[acl_key],\
                        self.group_for_nodes_if_tag_exists_dict) and \
                        self.tag_length_of_nodes_that_have_acls == \
                        self.tag_length_of_nodes:
                    allowed = True
                    message = 'Group ACL for %s %s %s %s %s'%\
                            (self.user.username, self.tag.tag,
                                    'exists for all the nodes in this tag.',
                                    'This Tag should have an ACL instead',
                                    'of the nodes.')
                    acl.append(self._return_node_or_tag_json(
                        self.user.username, 'Node Group ACL', len(self.tags),
                        self.tag_length_of_nodes_that_have_acls,
                        ','.join(self.tag_names), ','.join(self.group_names),
                        acl_key, allowed, message)
                        )

            if self.tags_for_group_exists:
                if True in map(lambda uid: uid[acl_key],\
                        self.tags_for_group_exists_dict):
                    allowed = True
                    message = 'Group ACL for %s exists on a tag'%\
                            (self.user.username,)
                    acl.append(self._return_node_or_tag_json(
                        self.user.username, 'Tag Group ACL', len(self.tags),
                        self.tag_length_of_nodes_that_have_acls,
                        ','.join(self.tag_names), ','.join(self.group_names),
                        acl_key, allowed, message)
                        )

        return(acl)


    def _return_node_or_tag_json(self, username, vtype, 
            nodes_in_tag, nodes_in_tag_acl,
            tagnames, groups, action, allowed, message):
        return({
            'user': username,
            'verification_type': vtype,
            'nodes_in_tag': nodes_in_tag,
            'nodes_in_tag_that_have_acl': nodes_in_tag_acl,
            'tag_names': tagnames,
            'groups': groups,
            'acl_action': action,
            'action_allowed': allowed,
            'message': message
            })

    def _return_global_json(self, username, vtype, groups, action, allowed,
            message):
        return({
            'user': username,
            'verification_type': vtype,
            'groups': groups,
            'acl_action': action,
            'action_allowed': allowed,
            'message': message
            })
