#!/usr/bin/env python                                                                                                                            
from datetime import datetime
from socket import getfqdn
from models.base import Base
from models.account import *
from models.packages import *
from models.node import *
from models.tagging import *
from models.scheduler import *
from models.ssl import *
from models.snapshots import *
from utils.common import *
from db.client import *


def user_exists(session, user_id=None, user_name=None):
    """
        return a user object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        user_id == the id of the user
        or
        user_name == the name of the user
    """
    session = validate_session(session)
    if user_id:
        user = session.query(Users).filter_by(id=user_id)
    elif user_name:
        user = session.query(Users).filter_by(username=user_name)
    user_exists = user.first()
    return(user_exists)


def tag_exists(session, tag_id=None, tag_name=None):
    """
        return a tag object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        tag_id == the id of the tag
        or
        tag_name == the name of the tag
    """
    session = validate_session(session)
    if tag_id:
        tag = session.query(TagInfo).filter(TagInfo.id == tag_id)
    elif tag_name:
        tag = session.query(TagInfo).filter(TagInfo.tag == tag_name)
    tag_exists = tag.first()
    return(tag_exists)


def node_exists(session, node_ip=None, node_id=None):
    """
        return a node object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        node_id == the id of the node
        or
        node_ip == the ip of the node
    """
    session = validate_session(session)
    node = None
    if not node_id:
        node = \
            session.query(NodeInfo).filter_by(ip_address=node_ip)
    else:
        node = \
            session.query(NodeInfo).filter_by(id=node_id)
    node_exists = node.first()
    return(node_exists)


def snapshots_exist(session, node_id=None):
    session = validate_session(session)
    if node_id:
        snapshots = session.query(SnapshotsPerNode).\
            filter(SnapshotsPerNode.node_id == node_id).all()
    return(snapshots)


def operation_exists(session, oper_id):
    """
        return a node object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        oper_id == the id of the operation
    """
    session = validate_session(session)
    oper = \
        session.query(Operations).filter_by(id=oper_id)
    oper_exists = oper.first()
    return(oper_exists)


def time_block_exists(session, id=None, label=None):
    """
        return a timeblock object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        id == the id of the timeblock
        or
        label == the name of the timeblock
    """
    session = validate_session(session)
    if id:
        tb_object = \
            session.query(TimeBlocker).filter_by(id=id)
        tb = tb_object.first()
    elif label:
        tb_object = \
            session.query(TimeBlocker).filter_by(name=label)
        tb = tb_object.first()
    return(tb)


def time_block_exists_today(session, start_date=None, start_time=None):
    """
        return a timeblock object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        start_date == the datetime date object of the start_date 
        of the timeblock
        start_time == the datetime time object of the start_time 
        of the timeblock
    """
    session = validate_session(session)
    if start_date and start_time:
        tbs = \
            session.query(TimeBlocker).\
                filter(TimeBlocker.start_time <= start_time).\
                filter(TimeBlocker.end_time >= start_time).\
                filter(TimeBlocker.start_date <= start_date).\
                filter(TimeBlocker.enabled == True).\
                filter(TimeBlocker.end_date == None).all()
        if len(tbs) == 0:
            tbs = \
                session.query(TimeBlocker).\
                    filter(TimeBlocker.start_time <= start_time).\
                    filter(TimeBlocker.end_time >= start_time).\
                    filter(TimeBlocker.start_date <= start_date).\
                    filter(TimeBlocker.enabled == True).\
                    filter(TimeBlocker.end_date >= start_date).all()
        elif len(tbs) == 0:
            tbs = \
                session.query(TimeBlocker).\
                    filter(TimeBlocker.start_time <= start_time).\
                    filter(TimeBlocker.start_date <= start_date).\
                    filter(TimeBlocker.enabled == True).\
                    filter(TimeBlocker.end_date >= start_date).all()
        today_is_blocked = False
        for tb in tbs:
            if tb:
                days_blocked, days_not_blocked = return_days(tb.days)
                for day in days_blocked:
                    if week_day[day] == str(start_date.weekday()):
                        today_is_blocked = True
                        json_out = {
                                   "pass" : False,
                                    "message" : "Time Block %s exists for this time frame" % (tb.name)
                                   }
                        return(today_is_blocked, tb, json_out)
        json_out = {
                    "pass" : True,
                    "message" : "Time Block does not exists for this time frame %s" % (start_date.strftime('%m/%d/%Y'))
                   }
        return(today_is_blocked, "No time blocks were found", json_out)


def operation_exists_using_node_id(session, node_id, oper_type):
    """
        return an operation object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        node_id == the id of the node
        oper_type == reboot|install|uninstall|etc.. operation_type
    """
    session = validate_session(session)
    oper = \
        session.query(Operations).\
                filter_by(node_id=node_id).\
                filter_by(results_received=None).\
                filter_by(operation_type=oper_type)
    oper_exists = oper.first()
    return(oper_exists)


def csr_exists(session, ip):
    """
        return a csr object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        ip == the ip of the node
    """
    session = validate_session(session)
    csr = \
        session.query(CsrInfo).filter_by(ip_address=ip)
    csr_exists = csr.first()
    return(csr_exists)


def cert_exists(session, node_id):
    """
        return a signed cert object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        node_id == the id of the node
    """
    session = validate_session(session)
    cert = \
        session.query(SslInfo).filter_by(node_id=node_id)
    cert_exists = cert.first()
    return(cert_exists)


def package_exists(session, tp_id):
    """
        return a package object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        tp_id == the toppatch_id of the package
    """
    session = validate_session(session)
    update = \
        session.query(Package).filter_by(toppatch_id=tp_id).first()
    return(update)


def node_package_exists(session, node, tp_id):
    """
        return a package object if it exist on a node, if not return None
        arguments below...
        session == SQLAlchemy Session
        node_id == the node_id of the node
        tp_id == the toppatch_id of the package
    """
    session = validate_session(session)
    update = \
        session.query(PackagePerNode).filter_by(node_id=node).\
                filter_by(toppatch_id=tp_id)
    update_exists = update.first()
    return(update_exists)


def software_exists(session, sname, sversion):
    """
        return a software object if it exist, if not return None
        arguments below...
        session == SQLAlchemy Session
        sname == the name of the software
        sversion == the version of the software
    """
    session = validate_session(session)
    software = \
        session.query(SoftwareAvailable).filter_by(name=sname).\
                filter_by(version=sversion).first()
    return(software)


def node_software_exists(session, sid):
    """
        return a software object if it exist on a node, if not return None
        arguments below...
        session == SQLAlchemy Session
        sid == the id of the software
    """
    session = validate_session(session)
    software = \
        session.query(SoftwareInstalled).filter_by(id=sid).first()
    return(software)


def get_transactions(session, count=None, offset=0):
    """
        return a list of RV Transactions
        arguments below...
        session == SQLAlchemy Session
        count == the total number of results you want returned, default == all
        offset == the offset number ofthe total you want to return
    """
    session = validate_session(session)
    all_operations = None
    total_count = 0
    if count and offset:
        all_operations = session.query(Operations).\
                order_by(Operations.operation_sent.desc()).\
                limit(count).offset(offset).all()
        total_count = session.query(Operations).\
                order_by(Operations.operation_sent.desc()).count()
    else:
        all_operations = session.query(Operations).\
                order_by(Operations.operation_sent.desc()).all()
        total_count = session.query(Operations).\
                order_by(Operations.operation_sent.desc()).count()
    all_results = session.query(Results).all()
    results_db = {}
    all_db = {}
    for operation in all_operations:
        all_db[str(operation.id)] = [operation]
    for results in all_results:
        if str(results.operation_id) in all_db:
            all_db[str(results.operation_id)].append(results)
    print all_db
    unsorted_list = []
    for key, value in all_db.items():
        unsorted_list.append((int(key), value))
    sorted_list = sorted(unsorted_list, key=lambda x: x[0])
    sorted_list.reverse()
    return(sorted_list, total_count)


