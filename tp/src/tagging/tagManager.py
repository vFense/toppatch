#!/usr/bin/env python

from db.query_table import *
from db.update_table import *
from utils.common import *

from models.account import *
from models.tagging import *
from models.packages import *
from models.node import *


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
    update_tag_stats(session)
    result = {}
    list_of_tags = []
    tag_stats = []
    count = None
    if tagid:
        tag_stats = session.query(TagStats, TagInfo).join(TagInfo).\
                filter(TagInfo.id == tagid).all()
    elif tagname:
        tag_stats = session.query(TagStats, TagInfo).join(TagInfo).\
                filter(TagInfo.tag == tagname).all()
    else:
        tag_stats = session.query(TagStats, TagInfo).join(TagInfo)
        count = tag_stats.count()
        tag_stats = tag_stats.all()
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
    if count:
        result['data'] = list_of_tags
        result['count'] = count
        return result
    else:
        return list_of_tags


def tag_adder(session, msg, username=None):
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


def tag_add_per_node(session, msg, username=None):
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
        user = session.query(User).filter_by(username=user_name).first()
        if user:
            tag_out = add_tag_per_node(session, nodes,
                    tag_name=tag_name, user_id=user.id,
                    username=username)
            tagged = {
                     "pass" : tag_out[0],
                     "message" : tag_out[1]
                     }
        update_tag_stats(session)
        return tagged


def tag_remove_per_node(session, msg, username=None):
    """
        Remove a node from an existing tag.
    """
    valid, json_msg = verify_json_is_valid(msg)
    if valid:
        if 'tag' in json_msg:
            tag_name = json_msg['tag']
        if 'nodes' in json_msg:
            nodes = json_msg['nodes']
        tag_out = remove_nodes_from_tag(session, tag_name, nodes=nodes)
        tagged = {
                 "pass" : tag_out[0],
                 "message" : tag_out[1]
                 }
        update_tag_stats(session)
        return tagged


def tag_remove(session, msg, username=None):
    """
        Remove a tag from RV
    """
    valid, json_msg = verify_json_is_valid(msg)
    if valid:
        if 'tag' in json_msg:
            tag = json_msg['tag']
        nodes_removed_from_tag = remove_all_nodes_from_tag(session, tag)
        tag_out = remove_tag(session, tag)
        if tag_out[0]:
            tagged = {
                     "pass" : tag_out[0],
                     "message" : tag_out[1]
                     }
            update_tag_stats(session)
            return tagged
        else:
            tagged = {
                     "pass" : nodes_removed_from_tag[0],
                     "message" : nodes_removed_from_tag[1]
                     }
            update_tag_stats(session)
            return tagged


def get_and_parse_tag_packages(session, node_ids, status):
    packages = []
    if 'available' in status:
        pkg_sub_query = session.query(PackagePerNode).\
                filter(PackagePerNode.installed == False).\
                filter(PackagePerNode.node_id.in_(node_ids)).\
                group_by(PackagePerNode.toppatch_id).subquery()

    elif 'installed' in status:
        pkg_sub_query = session.query(PackagePerNode).\
                filter(PackagePerNode.installed == True).\
                filter(PackagePerNode.node_id.in_(node_ids)).\
                group_by(PackagePerNode.toppatch_id).subquery()

    elif 'pending' in status:
        pkg_sub_query = session.query(PackagePerNode).\
                filter(PackagePerNode.installed == False).\
                filter(PackagePerNode.pending == True).\
                filter(PackagePerNode.node_id.in_(node_ids)).\
                group_by(PackagePerNode.toppatch_id).subquery()

    elif 'failed' in status:
        pkg_sub_query = session.query(PackagePerNode).\
                filter(PackagePerNode.installed == False).\
                filter(PackagePerNode.attempts > 0).\
                filter(PackagePerNode.node_id.in_(node_ids)).\
                group_by(PackagePerNode.toppatch_id).subquery()

    pkg_query = session.query(Package, pkg_sub_query).\
           join(pkg_sub_query).all()
    if len(pkg_query) >0:
        for pkg in pkg_query:
            if not pkg.Package.date_pub:
                date_pub = None
            else:
                date_pub = pkg.Package.date_pub.strftime('%m/%d/%Y %H:%M')
            packages.append({
                    'id': pkg.toppatch_id,
                    'description': pkg.Package.description,
                    #'description': pkg.Package.description.decode('utf-8', 'ignore'),
                    'severity': pkg.Package.severity,
                    'date_pub': date_pub,
                    'name': pkg.Package.name,
                    'kb': pkg.Package.kb,
                    'file_size': pkg.Package.file_size
                    })
    return(len(packages), packages)


def get_all_data_for_tag(session, tag_name=None, tag_id=None):
    tag = None
    nodes = []
    packages = []
    status = ['available', 'installed', 'pending', 'failed']
    tag_data = {}
    if tag_name:
        tag = session.query(TagInfo).filter(TagInfo.tag == tag_name).first()
    elif tag_id:
        tag = session.query(TagInfo).filter(TagInfo.id == tag_id).first()
    if tag:
        nodes_in_tag = session.query(TagsPerNode).\
                filter(TagsPerNode.tag_id == tag.id).all()
        if len(nodes_in_tag) >0:
            list_of_node_ids = map(lambda node: node.node_id, nodes_in_tag)
            list_of_nodes = session.query(NodeInfo, SystemInfo).\
                    join(SystemInfo).\
                    filter(NodeInfo.id.in_(list_of_node_ids)).all()
            for node in list_of_nodes:
                nodes.append({
                    'id': node[0].id,
                    'display_name': node[0].display_name,
                    'host_name': node[0].host_name,
                    'computer_name': node[0].computer_name,
                    'ip_address': node[0].ip_address,
                    'is_vm': node[0].is_vm,
                    'host_status': node[0].host_status,
                    'agent_status': node[0].agent_status,
                    'os_code': node[1].os_code,
                    'os_string': node[1].os_string,
                    'bit_type': node[1].bit_type,
                    'meta': node[1].meta,
                    })
            tag_data['node_count'] = len(nodes)
            tag_data['nodes'] = nodes
            for i in status:
                pkg_data = get_and_parse_tag_packages(session, list_of_node_ids, i)
                tag_data['packages_'+i+'_count'] = pkg_data[0]
                tag_data['packages_'+i] = pkg_data[1]
    return tag_data


