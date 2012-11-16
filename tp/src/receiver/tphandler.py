from json import loads, dumps
from jsonpickle import encode, decode
from datetime import datetime

from utils.db.update_table import *
from utils.db.query_table import *
from utils.db.client import *
from utils.common import verifyJsonIsValid
from utils.agentoperation import AgentOperation

OPERATION = 'operation'
OPERATION_ID = 'operation_id'
INSTALL = 'install'
UNINSTALL = 'uninstall'
UPDATES_PENDING = 'updates_pending'
UPDATES_INSTALLED = 'updates_installed'
REBOOT = 'reboot'
SOFTWARE_INSTALLED = 'system_applications'
SYSTEM_INFO = 'system_info'
STATUS_UPDATE = 'status'


class HandOff():
    def __init__(self, ENGINE, data, ip_address):
        self.session = createSession(ENGINE)
        self.data = data
        self.valid_json, self.json_object = verifyJsonIsValid(self.data)
        self.ip = ip_address
        if self.valid_json:
            exists, self.node = nodeExists(self.session,
                self.ip)
            if self.node:
                if self.node.last_agent_update == None:
                    self.dataCollector()
                    exists.update({"last_agent_update" : datetime.now(),
                                   "last_node_update" : datetime.now()
                                  })
                    TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)
            else:
                pass
            if self.json_object[OPERATION] == SYSTEM_INFO:
                addSystemInfo(self.session, self.json_object, self.node)
            if self.json_object[OPERATION] == UPDATES_PENDING or \
                    self.json_object[OPERATION] == UPDATES_INSTALLED:
                self.addUpdate()
            if self.json_object[OPERATION] == SOFTWARE_INSTALLED:
                self.softwareUpdate()
            if self.json_object[OPERATION] == STATUS_UPDATE:
                self.nodeUpdate()
            if self.json_object[OPERATION] == INSTALL:
                self.updateResults()
            if self.json_object[OPERATION] == UNINSTALL:
                self.updateResults()
            if self.json_object[OPERATION] == REBOOT:
                updateRebootStatus(self.session, exists)
            else:
                pass
        self.session.close()

    def dataCollector(self):
        operations = ["system_info", "updates_pending", 
                     "system_applications", "updates_installed"]
        lcollect = []
        for oper in operations:
            lcollect.append('{"node_id" : "%s", "operation" : "%s"}' \
                    % (self.node.id, oper)
                    )
        results = AgentOperation(lcollect)
        results.run()

    def addUpdate(self):
        addSoftwareUpdate(self.session, self.json_object)
        addUpdatePerNode(self.session, self.json_object)
        updateNodeStats(self.session, self.node.id)
        updateNetworkStats(self.session)
        TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)

    def softwareUpdate(self):
        os_code_exists = session.query(SystemInfo).filter_by(node_id=self.node.id).first()
        if os_code_exists:
            os_code = os_code_exists.os_code
            if os_code == "windows":
                addSoftwareAvailable(self.session, self.json_object)
                addSoftwareInstalled(self.session, self.json_object)
        updateNodeStats(self.session, self.node.id)
        updateNetworkStats(self.session)
        TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)

    def updateResults(self):
        results = addResults(self.session, self.json_object)
        updateNodeStats(self.session, self.node.id)
        updateNetworkStats(self.session)
        TcpConnect("127.0.0.1", "Connected", port=8080, secure=False)

    def nodeUpdate(self):
        results = updateNode(self.session, self.node.id)
