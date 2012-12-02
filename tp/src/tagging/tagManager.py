#!/usr/bin/env python

from db.query_table import *
from db.update_table import *
from utils.common import *

from models.account import *


def tag_lister(session):
    """
        return a list of tags in json
    """
    list_of_tags = []
    tags = session.query(TagInfo).all()
    for tag in tags:
        user = session.query(User).filter_by(id=tag.user_id).first()
        date_created = '%d/%d/%d' % (tag.date_created.month, \
                        tag.date_created.day, tag.date_created.year
                        )
        tag = {
                "tag_id" : tag.id,
                "tag_name" : tag.tag,
                "created_by" : user.username,
                "date_created" : date_created
              }
        list_of_tags.append(tag)
    return list_of_tags


def tag_list_by_nodes(session):
    """
        return a list of tags and the nodes associated with 
        the tag name in json
    """
    list_of_tags = []
    tags = session.query(TagInfo).all()
    for tag in tags:
        list_of_nodes = []
        nodes = session.query(TagsPerNode).filter_by(tag_id=tag.id).all()
        for node in nodes:
            node = session.query(NodeInfo).filter_by(id=node.node_id).first()
            list_of_nodes.append(node.ip_address)
        tag = {
                "tag_id" : tag.id,
                "tag_name" : tag.tag,
                "nodes" : list_of_nodes
              }
        list_of_tags.append(tag)
    return list_of_tags


def get_tag_stats(session, tagid=None, tagname=None):
    """
        return a list of tag_statistics in json
    """
    list_of_tags = []
    tag_stats = []
    if tagid:
        tag_stats = session.query(TagStats, TagInfo).\
                filter(TagInfo.id == tagid).all()
    elif tagname:
        tag_stats = session.query(TagStats, TagInfo).join(TagInfo).\
                filter(TagInfo.tag == tagname).all()
    else:
        tag_stats = session.query(TagStats, TagInfo).join(TagInfo).all()
    if len(tag_stats) > 0:
        for tags in tag_stats:
            tag = {
                    "tag_id" : int(tags[0].tag_id),
                    "tag_name" : tags[1].tag,
                    "reboots_pending" : int(tags[0].reboots_pending),
                    "agents_down" : int(tags[0].agents_down),
                    "agents_up" : int(tags[0].agents_up),
                    "patches_completed" : int(tags[0].patches_installed),
                    "patches_available" : int(tags[0].patches_available),
                    "patches_failed" : int(tags[0].patches_failed),
                    "patches_pending" : int(tags[0].patches_pending)
                }
        list_of_tags.append(tag)
    return list_of_tags


def tag_adder(session, msg):
    """
        add a new tag to RV
    """
    valid, json_msg = verify_json_is_valid(msg)
    if valid:
        if 'user' in json_msg:
            user_name = json_msg['user']
        if 'tag' in json_msg:
            tag_name = json_msg['tag']
        user = session.query(User).filter_by(username=user_name).first()
        if user:
            tag_out = add_tag(session, tag_name=tag_name, user_id=user.id)
            tagged = {
                     "pass" : tag_out[0],
                     "message" : tag_out[1]
                     }
        update_tag_stats(session)
        return tagged


def tag_add_per_node(session, msg):
    """
        Add a node to an existing tag or 
        add a node to a new tag
    """
    valid, json_msg = verify_json_is_valid(msg)
    if valid:
        if 'user' in json_msg:
            user_name = json_msg['user']
        if 'tag' in json_msg:
            tag_name = json_msg['tag']
        if 'nodes' in json_msg:
            nodes = json_msg['nodes']
        print msg
        user = session.query(User).filter_by(username=user_name).first()
        if user:
            tag_out = add_tag_per_node(session, nodes,
                    tag_name=tag_name, user_id=user.id)
            tagged = {
                     "pass" : tag_out[0],
                     "message" : tag_out[1]
                     }
        update_tag_stats(session)
        return tagged


def tag_remove_per_node(session, msg):
    """
        Remove a node from an existing tag.
    """
    valid, json_msg = verify_json_is_valid(msg)
    if valid:
        if 'tag' in json_msg:
            tag_name = json_msg['tag']
        if 'nodes' in json_msg:
            nodes = json_msg['nodes']
        print msg
        tag_out = remove_nodes_from_tag(session, tag_name, nodes=nodes)
        tagged = {
                 "pass" : tag_out[0],
                 "message" : tag_out[1]
                 }
        update_tag_stats(session)
        return tagged


def tag_remove(session, msg):
    """
        Remove a tag from RV
    """
    valid, json_msg = verify_json_is_valid(msg)
    if valid:
        if 'tag' in json_msg:
            tag = json_msg['tag']
        print json_msg
        nodes_removed_from_tag = remove_all_nodes_from_tag(session, tag)
        print nodes_removed_from_tag
        tag_out = remove_tag(session, tag)
        if tag_out[0]:
            tagged = {
                     "pass" : tag_out[0],
                     "message" : tag_out[1]
                     }
            print tag_out[2]
            return tagged
        else:
            tagged = {
                     "pass" : nodes_removed_from_tag[0],
                     "message" : nodes_removed_from_tag[1]
                     }
            return tagged

 
