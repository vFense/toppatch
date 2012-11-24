#!/usr/bin/env python

from utils.db.query_table import *
from utils.db.update_table import *
from utils.common import *

from models.account import *


def tagLister(session):
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

def tagListByNodes(session):
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



def tagAdder(session, msg):
    valid, json_msg = verifyJsonIsValid(msg)
    if valid:
        if 'user' in json_msg:
            user_name = json_msg['user']
        if 'tag' in json_msg:
            tag_name = json_msg['tag']
        user = session.query(User).filter_by(username=user_name).first()
        if user:
            tag_out = addTag(session, tag_name=tag_name, user_id=user.id)
            tagged = {
                     "pass" : tag_out[0],
                     "message" : tag_out[1]
                     }
        updateTagStats(session)
        return tagged

def tagAddPerNode(session, msg):
    valid, json_msg = verifyJsonIsValid(msg)
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
            tag_out = addTagPerNode(session, nodes, tag_name=tag_name, user_id=user.id)
            tagged = {
                     "pass" : tag_out[0],
                     "message" : tag_out[1]
                     }
        updateTagStats(session)
        return tagged

def tagRemovePerNode(session, msg):
    valid, json_msg = verifyJsonIsValid(msg)
    if valid:
        if 'tag' in json_msg:
            tag_name = json_msg['tag']
        if 'nodes' in json_msg:
            nodes = json_msg['nodes']
        print msg
        tag_out = removeNodesFromTag(session, tag_name, nodes=nodes)
        tagged = {
                 "pass" : tag_out[0],
                 "message" : tag_out[1]
                 }
        updateTagStats(session)
        return tagged

def tagRemove(session, msg):
    valid, json_msg = verifyJsonIsValid(msg)
    if valid:
        if 'tag' in json_msg:
            tag = json_msg['tag']
        print msg
        nodes_removed_from_tag = removeAllNodesFromTag(session, tag)
        print nodes_removed_from_tag
        tag_out = removeTag(session, tag)
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
 
