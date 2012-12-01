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
from utils.common import *
from db.client import *


def user_exists(session, user_id=None, user_name=None):
    session = validate_session(session)
    if user_id:
        user = session.query(Users).filter_by(id=user_id)
    elif user_name:
        user = session.query(Users).filter_by(username=user_name)
    user_exists = user.first()
    return(user_exists)


def tag_exists(session, tag_id=None, tag_name=None):
    session = validate_session(session)
    if tag_id:
        tag = session.query(TagInfo).filter(TagInfo.id == tag_id)
    elif tag_name:
        tag = session.query(TagInfo).filter(TagInfo.tag == tag_name)
    tag_exists = tag.first()
    return(tag_exists)


def node_exists(session, node_ip=None, node_id=None):
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


def operation_exists(session, oper_id):
    session = validate_session(session)
    oper = \
        session.query(Operations).filter_by(id=oper_id)
    oper_exists = oper.first()
    return(oper_exists)


def time_block_exists(session, id=None, label=None,
                    start_date=None, start_time=None):
    session = validate_session(session)
    if id:
        tb_object = \
            session.query(TimeBlocker).filter_by(id=id)
        tb = tb_object.first()
    return(tb)


def time_block_exists_today(session, start_date=None, start_time=None):
    session = validate_session(session)
    if start_date and start_time:
        tbs = \
            session.query(TimeBlocker).\
                filter(TimeBlocker.start_time <= start_time).\
                filter(TimeBlocker.end_time >= start_time).\
                filter(TimeBlocker.start_date <= start_date).\
                filter(TimeBlocker.end_date == None).all()
        if len(tbs) == 0:
            tbs = \
                session.query(TimeBlocker).\
                    filter(TimeBlocker.start_time <= start_time).\
                    filter(TimeBlocker.end_time >= start_time).\
                    filter(TimeBlocker.start_date <= start_date).\
                    filter(TimeBlocker.end_date >= start_date).all()
        elif len(tbs) == 0:
            tbs = \
                session.query(TimeBlocker).\
                    filter(TimeBlocker.start_time <= start_time).\
                    filter(TimeBlocker.start_date <= start_date).\
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
    session = validate_session(session)
    oper = \
        session.query(Operations).\
                filter_by(node_id=node_id).\
                filter_by(results_received=None).\
                filter_by(operation_type=oper_type)
    oper_exists = oper.first()
    return(oper_exists)


def csr_exists(session, node):
    session = validate_session(session)
    csr = \
        session.query(CsrInfo).filter_by(ip_address=node)
    csr_exists = csr.first()
    return(csr_exists)


def cert_exists(session, node):
    session = validate_session(session)
    cert = \
        session.query(SslInfo).filter_by(node_id=node)
    cert_exists = cert.first()
    return(cert_exists)


def update_exists(session, tp_id):
    session = validate_session(session)
    update = \
        session.query(Package).filter_by(toppatch_id=tp_id).first()
    return(update)


def node_update_exists(session, node, tp_id):
    session = validate_session(session)
    update = \
        session.query(PackagePerNode).filter_by(node_id=node).\
                filter_by(toppatch_id=tp_id)
    update_exists = update.first()
    return(update_exists)


def software_exists(session, sname, sversion):
    session = validate_session(session)
    software = \
        session.query(SoftwareAvailable).filter_by(name=sname).\
                filter_by(version=sversion).first()
    return(software)


def node_software_exists(session, sid):
    session = validate_session(session)
    software = \
        session.query(SoftwareInstalled).filter_by(id=sid).first()
    return(software)


def get_transactions(session, count=None, offset=0):
    #session.query(Operations, Results).filter(Results.id == Operations.results_id).all()
    all_operations = None
    total_count = 0
    if count and offset:
        all_operations = session.query(Operations).\
                order_by(Operations.operation_sent.desc()).\
                limit(count).offset(offset)
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
        results_db[str(results.id)] = [results]
    for operation in all_operations:
        if operation.results_id:
            all_db[str(operation.id)].append(results_db[str(operation.results_id)])
    unsorted_list = []
    for key, value in all_db.items():
        unsorted_list.append((int(key), value))
    sorted_list = sorted(unsorted_list, key=lambda x: x[0])
    sorted_list.reverse()
    return(sorted_list, total_count)


