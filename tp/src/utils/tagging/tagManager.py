#!/usr/bin/env python

from utils.db.query_table import *
from utils.db.update_table import *
from utils.common import *



def tagLister(session):
    tags = session.query(TagInfo).all()

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

def tagAddPerNode(session, msg):
    valid, json_msg = verifyJsonIsValid(msg)
    if valid:
        if 'user' in json_msg:
            user_name = json_msg['user']
        if 'tag' in json_msg:
            tag_name = json_msg['tag']
        if 'nodes' in json_msg:
            nodes = json_msg['nodes']
        user = session.query(User).filter_by(username=user_name).first()
        if user:
            tag_out = addTagPerNode(session, nodes, tag_name=tag_name, user_id=user.id)
