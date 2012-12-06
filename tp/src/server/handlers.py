
import tornado.web
import tornado.websocket
import re
try: import simplejson as json
except ImportError: import json
from models.node import NodeInfo
from db.client import *
from networking.agentoperation import AgentOperation
from scheduler.jobManager import job_scheduler, job_lister
from server.decorators import authenticated_request
from jsonpickle import encode

LISTENERS = []

class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        #self.clear_all_cookies()
        return self.get_secure_cookie("user")

class RootHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.render('../wwwstatic/index.html')


class LoginHandler(BaseHandler):
    def get(self):
        self.render('../wwwstatic/login.html')

    def post(self):
        username = self.get_argument("name", None);
        password = self.get_argument("password", None);
        if username is not None and password is not None:
            if self.application.account_manager.authenticate_account(str(self.get_argument("name")), str(self.get_argument("password"))):
                self.set_secure_cookie("user", self.get_argument("name"))
                redirect = self.get_argument("next", None)
                if redirect is not None:
                    self.redirect("/" + redirect)
                else:
                    self.redirect("/")
            else:
                 self.write("Invalid username and/or password .")
                 self.redirect("/login")
        else:
            self.write("Username and password can't be empty.")
            self.redirect("/login")



class SignupHandler(BaseHandler):
    def get(self):
        self.write('<html>'
                   '<body>'
                   '<form action="/signup" method="post">'
                   'Name: <input type="text" name="name">'
                   'Password: <input type="password" name="password">'
                   '<input type="submit" value="Sign up">'
                   '</form>'
                   '<a href="/login">Login</a>'
                   '</body></html>')


    def post(self):
        username = self.get_argument("name", None)
        password = self.get_argument("password", None)
        user = self.application.account_manager.user_account(str(username), str(password))

        if user is not None:
            self.application.account_manager.save_account(user)
            self.set_secure_cookie("user", username)
            result = {"pass" : True,
                      "message" : "User %s has been created." %\
                                  (username)
            }
        else:
            result = {"pass" : False,
                      "message" : "User %s can't be created." %\
                                  (username)
            }
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))

class testHandler(BaseHandler):
    def get(self):
        self.render('../data/templates/websocket-test.html')

def SendToSocket(message):
    for socket in LISTENERS:
        socket.write_message(message)

class WebsocketHandler(BaseHandler, tornado.websocket.WebSocketHandler):
    @authenticated_request
    def open(self):
        LISTENERS.append(self)
        print 'new connection'

    def on_message(self, message):
        print 'message received %s' % message

    def on_close(self):
        print 'connection closed...'
        LISTENERS.remove(self)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect('/login')
        #self.write("Goodbye!" + '<br><a href="/login">Login</a>')

class DeveloperRegistrationHandler(BaseHandler):


    @authenticated_request
    def get(self):
        self.write('<html>'
                   '<body>'
                   '<form action="/developer" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Generate Tokens">'
                   '</form>'
                   '</body></html>')


    def post(self):

        dev = self.application.account_manager.dev_account(self.get_argument("name"))

        if dev is not None:

            self.application.account_manager.save_account(dev)
            self.write("For %s: Client_id:  %s client_secret: %s" % (dev.name, dev.client_id, dev.client_secret))
        else:
            self.write("Developer account already exist.")

class FormHandler(BaseHandler):
    @authenticated_request
    def get(self):
        self.write('Invalid submission')

    @authenticated_request
    def post(self):
        resultjson = []
        node = {}
        result = []
        try:
            nodes = self.request.arguments['node']
        except:
            nodes = None
        try:
            tags = self.request.arguments['tag']
        except:
            tags = None
        try:
            params = self.get_argument('params')
        except:
            params = None
        try:
            time = self.get_argument('time')
            schedule = self.get_argument('schedule')
            label = self.get_argument('label')
        except:
            time = None
            schedule = None
        try:
            throttle = self.get_argument('throttle')
        except:
            throttle = None
        if nodes or tags:
            operation = self.get_argument('operation')
            if time:
                node['schedule'] = schedule
                node['time'] = time
                node['label'] = label
            if throttle:
                node['cpu_throttle'] = throttle
            if operation == 'install' or operation == 'uninstall':
                patches = self.request.arguments['patches']
                if nodes:
                    for node_id in nodes:
                        node['node_id'] = node_id
                        node['operation'] = operation
                        node['data'] = list(patches)
                        resultjson.append(encode(node))
                elif tags:
                    for tag_id in tags:
                        node['tag_id'] = tag_id
                        node['operation'] = operation
                        node['data'] = list(patches)
                        resultjson.append(encode(node))
                if time:
                    result = job_scheduler(resultjson,
                            self.application.scheduler
                            )
                else:
                    operation_runner = AgentOperation(resultjson)
                    operation_runner.run()
                    result = operation_runner.json_out
                    print result
            elif operation == 'reboot':
                for node_id in nodes:
                    node['operation'] = operation
                    node['node_id'] = node_id
                    resultjson.append(encode(node))
                if time:
                    result = job_scheduler(resultjson,
                            self.application.scheduler
                            )
                else:
                    operation_runner = AgentOperation(resultjson)
                    operation_runner.run()
                    result = operation_runner.json_out
                    print result
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(result))
            print json.dumps(result)
            #self.write(json.dumps(resultjson))

        if params:
            resultjson = json.loads(params)
            operation_runner = AgentOperation(resultjson)
            operation_runner.run()

            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(resultjson))


class AdminHandler(BaseHandler):
    @authenticated_request
    def post(self):
        try:
            oldpassword = self.get_argument('old-password')
            newpassword = self.get_argument('new-password')
            password = self.get_argument('password')
        except:
            password = None
            oldpassword = None
            newpassword = None

        if password:
            username = self.current_user
            if self.application.account_manager.authenticate_account(str(username), str(oldpassword)):
                self.application.account_manager.change_user_password(str(username), str(password))
                result = { 'error': False, 'description': 'changed password' }
            else:
                result = {'error': True, 'description': 'invalid password'}
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result))

