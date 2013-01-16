#!/usr/bin/env python
from datetime import datetime
from jsonpickle import encode
import logging
import logging.config
from networking.tcpasync import *
from db.update_table import *
from db.query_table import *
from db.client import *
from utils.common import *
from models.tagging import *
#import gevent
from threading import Thread

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

OPERATION = 'operation'
INSTALL = 'install'
UNINSTALL = 'uninstall'
HIDE = 'hide'
SHOW = 'show'
REBOOT = 'reboot'
UPDATESINSTALLED = 'updates_installed'
UPDATESPENDING = 'updates_pending'
SYSTEMINFO = 'system_info'
SYSTEMAPPLICATIONS = 'system_applications'
UNIX_DEPENDENCIES = 'unix_dependencies'
START = 'start'
STOP = 'stop'
RESTART = 'restart'
DATA = 'data'
SCHEDULE = 'schedule'
TIME = 'time'
AGENT_MANAGED_PORT = 9005
AGENT_PORT = 9003
ALLOWED_OPERATIONS = [SYSTEMINFO, UPDATESINSTALLED,
                      UPDATESPENDING, SYSTEMAPPLICATIONS,
                      UNIX_DEPENDENCIES]
SCHEDULED_OPERATIONS = [INSTALL, UNINSTALL, HIDE, SHOW, REBOOT]

class AgentOperation():
    def __init__(self, system_list, username='system_user'):
        """
        This class will take a list and iterate through it.
        Through each iteration, the object in each array will
        be verified that it was sent as a valid Json object.
        Once each object has been verified, it will then update
        the operations table and make a secure socket call to the
        remote agent. Through the use of Gevent, we have made this 
        operation much quicker as well as much safer.

        This is the Class that is used for the sending of operations
        to the agents.
        You initialize the class than you run it
        agentoper = AgentOperation(json_msg)
        agentoper.run()
        """
        ENGINE = init_engine()
        self.session = create_session(ENGINE)
        self.session = validate_session(self.session)
        self.system_list = system_list
        self.total_nodes = None
        self.username = username
        self.results = {}
        self.json_out = {}
        self.message_sent = False
        if type(system_list) == list:
            logger.debug('%s - operation received was of type list'%\
                    (self.username)
                    )
            self.system_list = system_list
            self.total_nodes = len(self.system_list)
        else:
            json_valid, self.system_list = verify_json_is_valid(system_list)
            if type(self.system_list) != list:
                logger.debug('%s - operation received was of type string'%\
                    (self.username)
                    )
                self.system_list = [self.system_list]
        if type(self.system_list[0]) == dict:
            verify_obj = self.system_list[0]
        else:
            is_verified, verify_obj = verify_json_is_valid(self.system_list[0])
        logger.debug('%s - json received was validated'%\
                    (self.username)
                    )
        if 'tag_id' in verify_obj:
            logger.debug('%s - operation received, was for a tag'%\
                    (self.username)
                    )
            system_list = self.convert_tag_op_to_node_op(self.system_list)
            if len(system_list) > 0:
                self.system_list = system_list
            

    def run(self):
        self.results = []
        self.threads = []
        for node in self.system_list:
            if type(node) != dict:
                json_valid, jsonobject = verify_json_is_valid(node)
            else:
                json_valid = True
                jsonobject = node
            if json_valid:
                self.node_id = jsonobject['node_id']
                self.node = node_exists(self.session, node_id=self.node_id)
                if not self.node.agent_status:
                    if len(self.system_list) > 1:
                        self.json_out ={
                            "node_id" : self.node_id,
                            "message" : "Agent Down",
                            "error" : "Agent Down",
                            "pass" : False
                            }
                        return(self.json_out)
                self.oper_type = jsonobject[OPERATION]
                self.oper_id = self.create_new_operation(self.node_id,
                        self.oper_type, self.node.ip_address
                        )
                start_date = datetime.now()
                time_block_exists, time_block, time_block_results = \
                        time_block_exists_today(self.session, 
                                start_date=start_date.date(),
                                start_time=start_date.time()
                                )
                if self.oper_type in SCHEDULED_OPERATIONS and time_block_exists:
                    logger.debug('%s - TimeBlock exists on %s for operation %s' %\
                            (self.username, self.node.ip_address, self.oper_type)
                            )
                    self.session.close()
                    self.json_out = time_block_results
                    add_results_non_json(self.session, node_id=node.id,
                            oper_id=oper.id, error='Time Block Exists',
                            reboot=False, result=False,
                            results_received=datetime.now(),
                            username=self.username
                            )
                    return(self.json_out)
                if not DATA in jsonobject:
                    message = self.operation_creator(data_list=None)
                    if RESTART in self.oper_type or STOP in self.oper_type \
                            or START in self.oper_type:
                        connection = Thread(target=self.connect,
                                args=(message, self.oper_type,
                                    self.oper_id, AGENT_MANAGED_PORT)).start()
                    else:
                        connection = Thread(target=self.connect,
                                args=(message, self.oper_type,
                                    self.oper_id, AGENT_PORT)).start()
                elif DATA in jsonobject:
                    if type(jsonobject[DATA]) == list:
                        data = jsonobject[DATA]
                        message = self.operation_creator(data_list=data)
                        connection = Thread(target=self.connect,
                                args=(message, self.oper_type,
                                    self.oper_id, AGENT_PORT)).start()
                    else:
                        raise("You must pass an array")
        self.session.close()
        
    def operation_creator(self, data_list=None):
        """
        Build a valid Json object and than encode it. Once the 
        encoding is complete, we will than pass this message to
        the TcpConnect class.
        """
        self.json_to_be_sent = None
        if data_list == None:
            self.json_to_be_sent = {
                        "operation" : self.oper_type,
                        "operation_id" : self.oper_id
                     }
        else:
            self.json_to_be_sent = {
                        "operation" : self.oper_type,
                        "operation_id" : self.oper_id,
                        "data" : data_list
                     }
        msg = encode(self.json_to_be_sent) 
        msg = msg + '<EOF>'
        logger.debug('%s - messaged to be sent %s' %\
                (self.username, msg)
                )
        return(msg)

    def connect(self, msg, oper_type, oper_id, port=9003, secure=True):
        node = node_exists(self.session, node_id=self.node_id)
        response = None
        completed = False
        agent_status = None
        connect = None
        if node.agent_status:
            agent_status = True
            logger.debug('%s - connecting to agent %s on port %s' %\
                    (self.username, node.ip_address, str(port))
                    )
            self.message_sent = True
            self.json_out ={
                     "node_id" : node.id,
                     "operation_id" : oper_id,
                     "message" : 'message sent',
                     "error" : None,
                     "pass" : True
                     }
            connect = TcpConnect(node.ip_address,
                    msg, port=port, secure=secure)
        else:
            self.message_sent = False
            self.json_out ={
                     "node_id" : node.id,
                     "operation_id" : oper_id,
                     "message" : "Agent Down",
                     "error" : "Agent Down",
                     "pass" : False
                     }
            logger.debug('%s - cannot connect to agent %s, agent down' %\
                    (self.username, node.ip_address)
                    )
            add_results_non_json(self.session, node_id=node.id,
                    oper_id=oper.id, error='Agent Down',
                    reboot=False, result=False,
                    results_received=datetime.now(), username=self.username
                    )
        self.connection_parser(connect, node, oper_type, oper_id)

    def connection_parser(self, connect, node, oper_type, oper_id):
        completed = False
        if connect:
            completed = True
            if not connect.error and connect.read_data:
                response = verify_json_is_valid(connect.read_data)
                if response[1]['operation'] == 'received':
                    logger.info('%s - operation received from agent %s' %\
                        (self.username, node.ip_address)
                        )
                    completed = True
                    update_operation_row(self.session,
                            oper_id, oper_recv=True,
                            username=self.username)
                    if oper_type == 'reboot':
                        update_reboot_status(self.session,
                                node.id, oper_type,
                                username=self.username)
                    if 'data' in self.json_to_be_sent:
                        for patch in self.json_to_be_sent['data']:
                            if oper_type == 'install':
                                patcher = self.session.query(PackagePerNode).\
                                    filter_by(toppatch_id=patch).\
                                    filter_by(node_id=node.id)
                                patcher.update({"pending" : True})
                                self.session.commit()
                    update_node_stats(self.session, node.id)
                    update_network_stats(self.session)
                    update_tag_stats(self.session)
        return self.json_out


    def create_new_operation(self, node_id, oper_type, ipaddress):
        """
        Add a new operation to the operations table and
        return the autogenerated operation_id
        """
        logger.debug('%s - adding a new operation for %s: operation%s'% \
                (self.username, ipaddress, oper_type)
                )
        oper = add_operation(self.session, node_id, oper_type,
                    operation_sent=datetime.now(), username=self.username
                    )
        return oper.id


    def convert_tag_op_to_node_op(self, tag_op_list):
        node_op_list = []
        for oper in tag_op_list:
            if type(oper) != dict:
                is_valid, oper = verify_json_is_valid(oper)
            else:
                is_valid = True
                oper = oper
            if is_valid:
                tag_id = oper['tag_id']
                self.nodes = self.session.query(TagsPerNode).\
                        filter(TagsPerNode.tag_id == tag_id).all()
                if len(self.nodes) > 0:
                    for node in self.nodes:
                        node_dict = {}
                        for key, value in oper.items():
                            if 'tag_id' in key:
                                node_dict['node_id'] = str(node.node_id)
                            else:
                                node_dict[key] = value
                        node_op_list.append(node_dict)
        return(node_op_list)


