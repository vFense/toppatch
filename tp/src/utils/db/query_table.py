#!/usr/bin/env python                                                                                                                            


from datetime import datetime
from socket import getfqdn
from models.base import Base
from models.account import *
from models.windows import *
from models.linux import *
from models.node import *
from models.tagging import *
from models.scheduler import *
from models.ssl import *
from utils.common import *
from utils.db.client import *


def userExists(session, user_id=None, user_name=None):
    session = ValidateSession(session)
    if user_id:
        user = session.query(Users).filter_by(id=user_id)
    elif user_name:
        user = session.query(Users).filter_by(username=user_name)
    user_exists = user.first()
    return(user, user_exists)

def tagExists(session, tag_id=None, tag_name=None):
    session = ValidateSession(session)
    if tag_id:
        tag = session.query(TagInfo).filter_by(id=tag_id)
    elif tag_name:
        tag = session.query(TagInfo).filter_by(tag=tag_name)
    tag_exists = tag.first()
    return(tag, tag_exists)

def nodeExists(session, node_ip=None, node_id=None):
    session = ValidateSession(session)
    node = None
    if not node_id:
        node = \
            session.query(NodeInfo).filter_by(ip_address=node_ip)
    else:
        node = \
            session.query(NodeInfo).filter_by(id=node_id)
    exists = node.first()
    return(node, exists)

def operationExists(session, oper_id):
    session = ValidateSession(session)
    oper = \
        session.query(Operations).filter_by(id=oper_id)
    exists = oper.first()
    return(exists, oper)

def timeBlockExists(session, id=None, label=None, start_date=None, start_time=None):
    session = ValidateSession(session)
    if id:
        tb_object = \
            session.query(TimeBlocker).filter_by(id=id)
        tb = tb_object.first()
    return(tb_object, tb)

def timeBlockExistsToday(session, start_date=None, start_time=None):
    session = ValidateSession(session)
    if start_date and start_time:
        tb_object = \
            session.query(TimeBlocker).filter(TimeBlocker.start_time <= start_time).filter(TimeBlocker.end_time >= start_time)
        tbs = tb_object.all()
        today_is_blocked = False
        for tb in tbs:
            if tb:
                days_blocked, days_not_blocked = returnDays(tb.days)
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

def operationExistsUsingNodeId(session, node_id, oper_type):
    session = ValidateSession(session)
    oper = \
        session.query(Operations).filter_by(node_id=node_id).filter_by(results_received=None).filter_by(operation_type=oper_type)
    exists = oper.first()
    return(exists, oper)

def csrExists(session, node):
    session = ValidateSession(session)
    csr = \
        session.query(CsrInfo).filter_by(ip_address=node)
    exists = csr.first()
    return(exists, csr)

def certExists(session, node):
    session = ValidateSession(session)
    cert = \
        session.query(SslInfo).filter_by(node_id=node)
    exists = cert.first()
    return(exists, cert)

def updateExists(session, tp_id, os_code):
    session = ValidateSession(session)
    if os_code == "windows":
        os = WindowsUpdate
    elif os_code == "linux":
        os = LinuxPackage
    update = \
        session.query(os).filter_by(toppatch_id=tp_id).first()
    return(update)

def nodeUpdateExists(session, node, tp_id, os=None):
    session = ValidateSession(session)
    if os == "windows":
        update = \
            session.query(ManagedWindowsUpdate).filter_by(node_id=node).filter_by(toppatch_id=tp_id)
        exists = update.first()
    elif os == "linux":
        update = \
            session.query(ManagedLinuxPackage).filter_by(node_id=node).filter_by(toppatch_id=tp_id)
        exists = update.first()
    return(exists, update)

def softwareExists(session, sname, sversion):
    session = ValidateSession(session)
    software = \
        session.query(SoftwareAvailable).filter_by(name=sname).filter_by(version=sversion).first()
    return(software)

def nodeSoftwareExists(session, sid):
    session = ValidateSession(session)
    software = \
        session.query(SoftwareInstalled).filter_by(id=sid).first()
    return(software)
