from json import loads, dumps
from jsonpickle import encode, decode
from datetime import datetime
import logging
import logging.config
from db.update_table import *
from db.query_table import *
from db.client import *
from utils.common import verify_json_is_valid
from networking.agentoperation import AgentOperation


logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
logger = logging.getLogger('rvlistener')
OPERATION = 'operation'
OPERATION_ID = 'operation_id'
INSTALL = 'install'
UNINSTALL = 'uninstall'
UPDATES_PENDING = 'updates_pending'
UPDATES_INSTALLED = 'updates_installed'
REBOOT = 'reboot'
SOFTWARE_INSTALLED = 'system_applications'
UNIX_DEPENDENCIES = 'unix_dependencies'
SYSTEM_INFO = 'system_info'
STATUS_UPDATE = 'status'


class HandOff():
    """
        Anytime an agent communicates with the RV Application,
        it must come through rvlistener. Once rvlistener receives
        all the data from the agent, rvlistener will than pass the msg
        to rvhandler. RVhandler than acts as the traffic coordinator
        for the received message.
    """
    def __init__(self, ENGINE):
        self.session = create_session(ENGINE)
        self.session = validate_session(self.session)


    def run(self, data, ip_address):
        self.data = data
        self.valid_json, self.json_object = verify_json_is_valid(self.data)
        self.ip = ip_address
        if self.valid_json:
            self.node = node_exists(self.session,
                node_ip=self.ip)
            if self.node:
                if self.node.last_agent_update == None:
                    self.node.last_agent_update = datetime.now()
                    self.node.last_node_update = datetime.now()
                    self.session.commit()
                    TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)
            else:
                pass
            if self.json_object[OPERATION] == SYSTEM_INFO:
                add_system_info(self.session, self.json_object, self.node)
            if self.json_object[OPERATION] == UPDATES_PENDING or \
                    self.json_object[OPERATION] == UPDATES_INSTALLED:
                self.add_update()
            if self.json_object[OPERATION] == SOFTWARE_INSTALLED:
                self.software_update()
            if self.json_object[OPERATION] == UNIX_DEPENDENCIES:
                self.add_dependency()
            if self.json_object[OPERATION] == STATUS_UPDATE:
                self.node_update()
            if self.json_object[OPERATION] == INSTALL:
                self.update_results()
            if self.json_object[OPERATION] == UNINSTALL:
                self.update_results()
            if self.json_object[OPERATION] == REBOOT:
                update_reboot_status(self.session, exists)
            else:
                pass
        else:
            logger.info('Json is not valid %s' %\
                    (data)
                    )
        self.session.close()

    def get_data(self, oper):
        lcollect = []
        lcollect.append('{"node_id" : "%s", "operation" : "%s"}' \
                        % (self.node.id, oper)
                        )
        results = AgentOperation(lcollect)
        results.run()


    def add_update(self):
        logger.debug('Adding Software to package table')
        add_software_update(self.session, self.json_object)
        logger.debug('Adding Software Status to the package_per_node table %s' %\
                ('for node' % self.node.ip_address)
                )
        add_software_per_node(self.session, self.json_object)
        logger.debug('updateing node_stats for %s' % \
                (self.node.ip_address)
                )
        update_node_stats(self.session, self.node.id)
        logger.debug('updateing network_stats')
        update_network_stats(self.session)
        logger.debug('updateing tag_stats')
        update_tag_stats(self.session)
        TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)


    def software_update(self):
        os_code_exists = self.session.query(SystemInfo).\
                filter_by(node_id=self.node.id).first()
        if os_code_exists:
            os_code = os_code_exists.os_code
            if os_code == "windows":
                logger.debug('adding 3rd party software to'+\
                        ' software_available table')
                add_software_available(self.session, self.json_object)
                logger.debug('adding 3rd party software to'+\
                        ' software_installed table for node %s' %\
                        (self.node.ip_address)
                        )
                add_software_installed(self.session, self.json_object)
        logger.debug('updateing node_stats for %s' % \
                (self.node.ip_address)
                )
        update_node_stats(self.session, self.node.id)
        logger.debug('updateing network_stats')
        update_network_stats(self.session)
        logger.debug('updateing tag_stats')
        update_tag_stats(self.session)
        TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)


    def update_results(self):
        results = add_results(self.session, self.json_object)
        logger.debug('updateing node_stats for %s' % \
                (self.node.ip_address)
                )
        update_node_stats(self.session, self.node.id)
        logger.debug('updateing network_stats')
        update_node_stats(self.session, self.node.id)
        update_network_stats(self.session)
        logger.debug('updateing tag_stats')
        update_tag_stats(self.session)
        TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)


    def update_dependency(self):
        results = add_dependency(self.session, self.json_object)
        TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)


    def node_update(self):
        logger.debug('no status updated for node %s' % (self.node.ip_address))
        results = update_node(self.session, self.node.id, self.ip)


