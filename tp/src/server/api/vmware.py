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

logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvapi')

class CreateVmwareConfigHandler(BaseHandler):
    @authenticated_request
    def post(self):
        passed = False
        username = self.get_current_user()
        vm_host = self.get_argument('vmhost', None)
        vm_user = self.get_argument('user', None)
        vm_password = self.get_argument('password', None)
        snapshot = self.get_argument('snapshot', False)
        cycle = self.get_argument('cycle', '12h')
        if vm_host and vm_user and vm_password and \
                cycle_validator(cycle):
            vim = None
            try:
                vim = Vim(vm_host)
            except Exception as e:
                message = 'Invalid VM Host %s' % (vm_host)
                passed = False
            if vim:
                try:
                    vim.login(vm_user, vm_password)
                    create_vm_config(vm_host, vm_user, vm_password,
                            create_snapshot=snapshot, cycle=cycle)
                    message = 'Valid Host and Credentials'
                    passed = True
                except Exception as e:
                    message = 'Invalid username or password'
                    passed = False
        else:
            message = 'Invalid cycle: %s\n Valid cycle examples:%s' %\
                    (cycle, '12h or 3h 30m')
            passed = False
        result = {
                'pass': passed,
                'message': message
                }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class CreateSnapshotHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        self.session = self.application.session
        self.session = validate_session(self.session)
        vm_name = self.get_argument('vmname', None)
        snap_name = self.get_argument('snapname', None)
        memory = self.get_argument('memory', False)
        quiesce = self.get_argument('quiesce', False)
        snap_description = self.get_argument('description', None)
        result = None
        if vm_name and snap_name:
            vm = VmApi()
            result = vm.create_snapshot(vm_name=vm_name,
                    snap_name=snap_name, memory=memory,
                    quiesce=quiesce, snap_description=snap_description,
                    username=username
                    )
        else:
            result = {
                    'pass': False,
                    'message': 'Needed arguments: %s\n%s%s' % \
                            ('vnname and snapname',
                            'Optional arguments: ',
                            'memeory, queisce, description'
                            )
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class RevertSnapshotHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vmname', None)
        snap_name = self.get_argument('snapname', None)
        result = None
        if vm_name and snap_name:
            vm = VmApi()
            result = vm.revert_to_snapshot(vm_name=vm_name,
                    snap_name=snap_name, username=username
                    )
        else:
            result = {
                    'pass': False,
                    'message': 'Needed arguments: %s\n%s' % \
                            ('vnname and snapname')
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class RemoveSnapshotHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vmname', None)
        snap_name = self.get_argument('snapname', None)
        children = self.get_argument('children', True)
        result = None
        if vm_name and snap_name and children:
            vm = VmApi()
            result = vm.remove_snapshot(vm_name=vm_name,
                    snap_name=snap_name, remove_children=children,
                    username=username
                    )
        else:
            result = {
                    'pass': False,
                    'message': 'Needed arguments: %s\n%s' % \
                            ('vnname and snapname')
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class RemoveAllSnapshotsHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vmname', None)
        result = None
        if vm_name:
            vm = VmApi()
            result = vm.remove_all_snapshots(vm_name=vm_name,
                    username=username)
        else:
            result = {
                    'pass': False,
                    'message': 'Needed arguments: %s\n%s' % \
                            ('vnname and snapname')
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))
