import tornado.httpserver
import tornado.web
import functools

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
from db.client import *
from utils.common import *
from node.nodeManager import *
from logger.rvlogger import RvLogger
from user.manager import *
from virtual.vmware.vmapi import *
from virtual.vmware.vmcollector import *

from jsonpickle import encode

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class GetVmwareConfigHandler(BaseHandler):
    @authenticated_request
    def get(self):
        vm = VmApi()
        result = {
            'host': vm.host,
            'username': vm.username,
            'cycle': vm.cycle,
            'snapshot_before_patch': vm.create_snapshot_before_patch
            }
     
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class CreateVmwareConfigHandler(BaseHandler):
    @authenticated_request
    def post(self):
        passed = False
        logged_in = False
        session = self.application.session
        session = validate_session(session)
        username = self.get_current_user()
        vm_host = self.get_argument('vm_host', None)
        vm_user = self.get_argument('vm_user', None)
        vm_password = self.get_argument('vm_password', None)
        snapshot = self.get_argument('snapshot', False)
        cycle = self.get_argument('cycle', '12h')
        print vm_host, vm_user, vm_password, snapshot, cycle
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
                    message = 'Valid Host and Credentials'
                    passed = True
                    logged_in = True
                except Exception as e:
                    message = 'Invalid username or password'
                    passed = False
                    logger.info(e)
            if logged_in:
                create_vm_config(vm_host, vm_user, vm_password,
                        create_snapshot=snapshot, cycle=cycle)
                #tornado.ioloop.IOLoop.instance().\
                #        add_callback(functools.partial(
                #            get_vm_data, username
                #            ))
                sched = self.application.scheduler
                try:
                    sched.unschedule_func(get_vm_data)
                    logger.info('unschedule the vmware data collector')
                except Exception as e:
                    print e
                    logger.info(e)
                tornado.ioloop.IOLoop.instance().\
                        add_callback(functools.partial(
                            sched.add_interval_job,
                            get_vm_data,
                            args=[username],
                            name='vmware collector',
                            jobstore='toppatch',
                            **parse_interval(cycle)
                            ))

                #sched.add_interval_job(get_vm_data,
                #        args=[username],
                #        name='vmware collector',
                #        jobstore='toppatch',
                #        **parse_interval(cycle)
                #        )
        else:
            message = 'Invalid cycle: %s\n Valid cycle examples:%s' %\
                    (cycle, '12h or 3h 30m')
            passed = False
        result = {
                'pass': passed,
                'message': message
                }
        session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class CreateSnapshotHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vm_name', None)
        snap_name = self.get_argument('snap_name', None)
        memory = self.get_argument('memory', False)
        quiesce = self.get_argument('quiesce', False)
        if memory:
            memory = return_bool(memory)
        if quiesce:
            quiesce = return_bool(quiesce)
        snap_description = self.get_argument('snap_description', '')
        result = None
        if vm_name and snap_name:
            vm = VmApi()
            if vm.config_exists:
                vm.connect()
                if vm.logged_in:
                    tornado.ioloop.IOLoop.instance().add_callback(functools.partial(vm.create_snapshot,
                            **{'vm_name':vm_name,
                                'snap_name':snap_name,
                                'memory':memory,
                                'quiesce':quiesce,
                                'snap_description':snap_description,
                                'username':username}
                            ))
                    result = {
                            'pass': True,
                            'message': 'Create SnapShot Operation In Progress'
                            }
                else:
                    result = {
                            'pass': False,
                            'message': 'Vcenter is not responding'
                            }
            else:
                result = {
                        'pass': False,
                        'message': 'VMWare Config Does Not Exist'
                        }
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
        print result
        self.write(json.dumps(result, indent=4))


class RevertSnapshotHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vm_name', None)
        snap_name = self.get_argument('snap_name', None)
        result = None
        if vm_name and snap_name:
            vm = VmApi()
            if vm.config_exists:
                vm.connect()
                if vm.logged_in:
                    tornado.ioloop.IOLoop.instance().\
                            add_callback(functools.partial(vm.revert_to_snapshot,
                            **{'vm_name':vm_name,
                                'snap_name':snap_name,
                                'username':username}
                            ))
                    result = {
                            'pass': True,
                            'message': 'Revert To SnapShot Operation In Progress'
                            }
                else:
                    result = {
                            'pass': False,
                            'message': 'Vcenter is not responding'
                            }
            else:
                result = {
                        'pass': False,
                        'message': 'VMWare Config Does Nto Exists'
                        }
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
        vm_name = self.get_argument('vm_name', None)
        snap_name = self.get_argument('snap_name', None)
        children = self.get_argument('children', True)
        if type(children) != bool:
            children = return_bool(children)
        result = None
        if vm_name and snap_name and children:
            vm = VmApi()
            if vm.config_exists:
                vm.connect()
                if vm.logged_in:
                    tornado.ioloop.IOLoop.instance().\
                            add_callback(functools.partial(vm.remove_snapshot,
                            **{'vm_name':vm_name,
                                'snap_name':snap_name,
                                'remove_children':children,
                                'username':username}
                            ))
                    result = {
                            'pass': True,
                            'message': 'Remove To SnapShot Operation In Progress'
                            }
                    print result
                else:
                    result = {
                            'pass': False,
                            'message': 'Vcenter is not responding'
                            }
            else:
                result = {
                        'pass': False,
                        'message': 'VMWare Config Does Not Exist'
                        }
        else:
            result = {
                    'pass': False,
                    'message': 'Missing Arguments'
                    }
        self.set_header('Content-Type', 'application/json')
        print result
        self.write(json.dumps(result, indent=4))


class RemoveAllSnapshotsHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vm_name', None)
        result = None
        if vm_name:
            vm = VmApi()
            if vm.config_exists:
                vm.connect()
                if vm.logged_in:
                    tornado.ioloop.IOLoop.instance().\
                            add_callback(functools.partial(
                                vm.remove_all_snapshots,
                                **{'vm_name':vm_name,
                                    'username':username}
                                ))
                    result = {
                            'pass': True,
                            'message': 'Removing All SnapShots In Progress'
                            }
                else:
                    result = {
                            'pass': False,
                            'message': 'Vcenter is not responding'
                            }
            else:
                result = {
                        'pass': False,
                        'message': 'VMWare Config Does Not Exist'
                        }
        else:
            result = {
                    'pass': False,
                    'message': 'Needed arguments: %s\n%s' % \
                            ('vnname and snapname')
                    }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class GetNodeSnapshotsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        result = None
        session = self.application.session
        session = validate_session(session)
        node_id = self.get_argument('node_id', None)
        vm_name = self.get_argument('vm_name', None)
        display_name = self.get_argument('display_name', None)
        host_name = self.get_argument('host_name', None)
        if node_id:
            result = get_snapshost_for_vm(session, node_id=node_id,
                    username=username)
        elif vm_name:
            node = session.query(NodeInfo).\
                    filter(NodeInfo.vm_name == vm_name).first()
            if node:
                result = get_snapshost_for_vm(session, node_id=node.id,
                        username=username)
        elif display_name:
            node = session.query(NodeInfo).\
                    filter(NodeInfo.display_name == display_name).first()
            if node:
                result = get_snapshost_for_vm(session, node_id=node.id,
                        username=username)
        elif host_name:
            node = session.query(NodeInfo).\
                    filter(NodeInfo.host_name == host_name).first()
            if node:
                result = get_snapshost_for_vm(session, node_id=node.id,
                        username=username)
        else:
            result = {
                    'pass': False,
                    'message': 'Optional arguments: %s\n' % \
                            ('nodeid or vmname or displayname or hostname')
                    }
        session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class GetNodeVmInfoHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        result = None
        session = self.application.session
        session = validate_session(session)
        node_id = self.get_argument('node_id', None)
        vm_name = self.get_argument('vm_name', None)
        display_name = self.get_argument('display_name', None)
        host_name = self.get_argument('host_name', None)
        if node_id:
            results = get_vm_info_from_db(session,\
                    node_id=node_id, username=username)
        elif vm_name:
            vm = session.query(VirtualMachineInfo).\
                    filter(VirtualMachineInfo.vm_name == vm_name).first()
            results = get_vm_info_from_db(session,\
                    node_id=vm.node_id, username=username)
        elif display_name:
            node = session.query(NodeInfo).\
                    filter(NodeInfo.display_name == display_name).first()
            results = get_vm_info_from_db(session,\
                    node_id=vm.node.id, username=username)
        elif host_name:
            node = session.query(NodeInfo).\
                    filter(NodeInfo.host_name == host_name).first()
            results = get_vm_info_from_db(session,\
                    node_id=vm.node.id, username=username)
        else:
            results = {
                'pass': False,
                'message': 'Invalid Arguments'
                }
        session.close()
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))



class PowerOnVmHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vm_name', None)
        results = None
        if vm_name:
            vm = VmApi()
            if vm.config_exists:
                vm.connect()
                if vm.logged_in:
                    results = vm.poweron_on(vm_name=vm_name, username=username)
                else:
                    results = {
                        'pass': False,
                        'message': 'Vcenter is not accessible'
                        }
            else:
                results = {
                     'pass': False,
                     'message': 'VMware is not configured in RV'
                     }
        else:
            results = {
                     'pass': False,
                     'message': 'Invalid Argument'
                     }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


class ShutdownVmHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vm_name', None)
        results = None
        if vm_name:
            vm = VmApi()
            if vm.config_exists:
                vm.connect()
                if vm.logged_in:
                    results = vm.shutdown_vm(vm_name=vm_name, username=username)
                else:
                    results = {
                        'pass': False,
                        'message': 'Vcenter is not accessible'
                        }
            else:
                results = {
                     'pass': False,
                     'message': 'VMware is not configured in RV'
                     }
        else:
            results = {
                     'pass': False,
                     'message': 'Invalid Argument'
                     }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))



class RebootVmHandler(BaseHandler):
    @authenticated_request
    def post(self):
        username = self.get_current_user()
        vm_name = self.get_argument('vm_name', None)
        results = None
        if vm_name:
            vm = VmApi()
            if vm.config_exists:
                vm.connect()
                if vm.logged_in:
                    results = vm.reboot_vm(vm_name=vm_name, username=username)
                else:
                    results = {
                        'pass': False,
                        'message': 'Vcenter is not accessible'
                        }
            else:
                results = {
                     'pass': False,
                     'message': 'VMware is not configured in RV'
                     }
        else:
            results = {
                     'pass': False,
                     'message': 'Invalid Argument'
                     }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


