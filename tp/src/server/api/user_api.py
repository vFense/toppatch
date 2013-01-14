import tornado.httpserver
import tornado.web

try: import simplejson as json
except ImportError: import json

import logging
import logging.config
from models.application import *
from server.decorators import authenticated_request
from server.handlers import BaseHandler, LoginHandler
from models.base import Base
from models.packages import *
from models.node import *
from models.ssl import *
from models.scheduler import *
from server.handlers import SendToSocket
from db.client import *
from scheduler.jobManager import job_lister, remove_job
from scheduler.timeBlocker import *
from tagging.tagManager import *
from search.search import *
from utils.common import *
from packages.pkgManager import *
from node.nodeManager import *
from transactions.transactions_manager import *
from logger.rvlogger import RvLogger
from user.manager import *
from sqlalchemy import distinct, func
from sqlalchemy.orm import sessionmaker, class_mapper

from jsonpickle import encode

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class ListUserHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        result = list_user(self.session)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class DeleteUserHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        user = None
        userid = self.get_argument('userid', None)
        username = self.get_argument('username', None)
        if userid:
            user = self.session.query(User).\
                    filter(User.id == userid).first()
            result = delete_user(self.session, user.id)
        elif username:
            user = self.session.query(User).\
                    filter(User.username == username).first()
            result = delete_user(self.session, user.id)
        else:
            result = {
                    'pass': False,
                    'message': 'Incorrect arguments passed. username or userid'
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))



class CreateUserHandler(BaseHandler):
    @authenticated_request
    def post(self):
        user_name = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        username = self.get_argument("name", None)
        email = self.get_argument("email", None)
        fullname = self.get_argument("fullname", None)
        password = self.get_argument("password", None)
        group = self.get_argument("group", 'READ_ONLY')

        if username and password and group:
            password = password.encode('utf8')
            user = self.session.query(User).\
                    filter(User.username == username).first()
            if not user:
                user_add = create_user(self.session, \
                        username=username, password=password,
                        fullname=fullname, email=email,
                        groupname=group)
                result = user_add
            else:
                result = {
                        'pass': False,
                        'message': 'User %s already exists' % (username)
                        }
        else:
            result = {"pass" : False,
                      "message" : "User %s can't be created, %s, %s %s" %\
                                  (username, 'Insufficient arguments',
                                      'arguments needed are ',
                                      'username, password, group')
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class ModifyUserFromGroupHandler(BaseHandler):
    def post(self):
        user_name = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        user_id = self.get_argument("user_id", None)
        username = self.get_argument("username", None)
        group_id = self.get_argument("group_id", None)
        groupname = self.get_argument("groupname", None)
        action = self.get_argument("action", None)
        if user_id and group_id:
            result = modify_user_from_group(self.session, 
                    user_id=user_id, group_id=group_id, action=action)
        elif username and groupname:
            user = self.session.query(User).\
                    filter(User.username == username).first()
            group = self.session.query(Group).\
                    filter(Group.groupname == groupname).first()
            result = modify_user_from_group(self.session, 
                    user_id=user.id, group_id=group.id, action=action)
        elif user_id and groupname:
            group = self.session.query(Group).\
                    filter(Group.groupname == groupname).first()
            result = modify_user_from_group(self.session, 
                    user_id=user_id, group_id=group.id, action=action)
        elif username and group_id:
            user = self.session.query(User).\
                    filter(User.username == username).first()
            result = modify_user_from_group(self.session, 
                    user_id=user.id, group_id=group_id, action=action)
        else:
            result = {
                    'pass': False,
                    'message': 'Incorrect Parameters were passed'
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class ListGroupHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.session = self.application.session
        self.session = validate_session(self.session)
        result = list_groups(self.session)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class CreateGroupHandler(BaseHandler):
    @authenticated_request
    def post(self):
        user_name = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        groupname = self.get_argument("groupname", None)
        acl_type = self.get_argument('acl_type', None)
        acl_action = 'create'
        acl = self.get_argument('acl', None)
        if groupname and acl_type and acl:
            group_exists = self.session.query(Group).\
                    filter(Group.groupname == groupname).first()
            if not group_exists:
                group = create_group(self.session, groupname)
                group_result = group
            else:
                group_result = {
                        'pass': False,
                        'message': 'Group %s already exists' % (groupname)
                        }
        else:
            result = {
                    'pass' : False,
                    'message' : 'Group %s can"t be created, %s, %s %s' %\
                                  (groupname, 'Insufficient arguments',
                                      'arguments needed are ',
                                      'groupname')
                    }
        if acl and group_result['pass']:
            valid_json, json_acl = verify_json_is_valid(acl)
            if acl_type and acl_action and acl and valid_json:
                json_acl['group_id'] = group_result['id']
                acl_result = \
                    acl_modifier(self.session, acl_type, acl_action, json_acl)
                if group_result['pass'] and acl_result['pass']:
                    result = {
                        'pass': True,
                        'message': 'Group and ACL created Successfully'
                    }
                else:
                    result = {
                        'pass': False,
                        'message': 'Group and ACL creation failed'
                    }
                    group_deleted = \
                            delete_group(self.session,
                                    group_id=group_result['id'])
        elif acl and not group_result['pass']:
            result = {
                    'pass': False,
                    'message': 'Incorrect arguments passed. %s:%s, %s, %s' %\
                            ('Arguments needed', 'acl_type', 'acl_action', 
                                'acl')
                    }
            group_deleted = delete_group(self.session,
                                    group_id=group_result['id'])
        else:
            result = {
                    'pass' : False,
                    'message' : 'Group %s can"t be created, %s, %s %s' %\
                                  (groupname, 'Insufficient arguments',
                                      'arguments needed are ',
                                      'groupname')
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(acl_result, indent=4))


class DeleteGroupHandler(BaseHandler):
    @authenticated_request
    def post(self):
        user_name = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        group = None
        groupid = self.get_argument('groupid', None)
        groupname = self.get_argument('groupname', None)
        if groupid:
            group = self.session.query(Group).\
                    filter(Group.id == groupid).first()
            result = delete_group(self.session, group_id=group.id)
        elif groupname:
            group = self.session.query(User).\
                    filter(Group.groupname == groupname).first()
            result = delete_group(self.session, group.id)
        else:
            result = {
                    'pass': False,
                    'message': 'Incorrect arguments passed. groupname or groupid'
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))



class AclModifierHandler(BaseHandler):
    @authenticated_request
    def post(self):
        user_name = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        acl_type = self.get_argument('acl_type', None)
        acl_action = self.get_argument('acl_action', None)
        acl = self.get_argument('acl', None)
        result = None
        print acl
        if acl:
            valid_json, json_acl = verify_json_is_valid(acl)
            if acl_type and acl_action and acl and valid_json:
                result = \
                    acl_modifier(self.session, acl_type, acl_action, json_acl)
        else:
            result = {
                    'pass': False,
                    'message': 'Incorrect arguments passed. %s:%s, %s, %s' %\
                            ('Arguments needed', 'acl_type', 'acl_action', 
                                'acl')
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


