
from time import sleep
import tornado.web
import tornado.websocket
import re
try: import simplejson as json
except ImportError: import json
from models.node import NodeInfo
from db.client import *
from user.manager import *
from networking.agentoperation import AgentOperation
from scheduler.jobManager import job_scheduler, job_lister
from server.decorators import authenticated_request
from jsonpickle import encode

class AgentOperationHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.write('Invalid submission')


    @authenticated_request
    def post(self):
        username = self.get_current_user()
        resultjson = []
        node = {}
        result = []
        nodes = self.get_arguments('node')
        if len(nodes) <1:
            nodes = None
        tags = self.get_arguments('tag')
        if len(tags) <1:
            tags = None
        params = self.get_argument('params', None)
        time = self.get_argument('time', None)
        schedule = self.get_argument('schedule', None)
        label = self.get_argument('label', None)
        throttle = self.get_argument('throttle', None)
        operation = self.get_argument('operation', None)
        patches = self.get_arguments('patches')
        if len(patches) <1:
            patches = None
        if nodes or tags:
            if time:
                node['schedule'] = schedule
                node['time'] = time
                node['label'] = label
            if throttle:
                node['cpu_throttle'] = throttle
            if operation == 'install' or operation == 'uninstall':
                if nodes:
                    for node_id in nodes:
                        node['node_id'] = node_id.encode('utf8')
                        node['operation'] = operation
                        node['data'] = patches
                        resultjson.append(encode(node))
                elif tags:
                    for tag_id in tags:
                        node['tag_id'] = tag_id.encode('utf8')
                        node['operation'] = operation
                        node['data'] = patches
                        resultjson.append(encode(node))
                if time:
                    result = job_scheduler(resultjson,
                            self.application.scheduler,
                            username=username
                            )
                else:
                    operation_runner = AgentOperation(resultjson,
                            username=username)
                    operation_runner.run()
                    while not operation_runner.json_out:
                        sleep(.50)
                    result = operation_runner.json_out
                    print result
            elif operation == 'reboot' or operation == 'restart' or\
                    operation == 'stop' or operation == 'start':
                for node_id in nodes:
                    node['operation'] = operation
                    node['node_id'] = node_id.encode('utf8')
                    resultjson.append(encode(node))
                if time:
                    result = job_scheduler(resultjson,
                            self.application.scheduler,
                            username=username
                            )
                else:
                    operation_runner = AgentOperation(resultjson,
                            username=username
                            )
                    operation_runner.run()
                    while not operation_runner.json_out:
                        sleep(.50)
                    result = operation_runner.json_out
                    print result
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(result))

        if params:
            resultjson = json.loads(params)
            operation_runner = AgentOperation(resultjson,
                    username=username)
            operation_runner.run()
            while not operation_runner.json_out:
                sleep(.50)
            result = operation_runner.json_out
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(result))



