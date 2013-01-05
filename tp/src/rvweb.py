"""
Main launching point of the Top Patch Server
"""
import base64
import uuid
import os
import threading
import logging
import logging.config
import gevent
from gevent import monkey
monkey.patch_all(thread=True)

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

from sqlalchemy.engine import *
from sqlalchemy.orm import *

from db.client import *
from server.handlers import RootHandler, LoginHandler, WebsocketHandler, testHandler, LogoutHandler, DeveloperRegistrationHandler, FormHandler, AdminHandler
from server.oauth.handlers import AuthorizeHandler, AccessTokenHandler

from server.api.user_api import *
from server.api.log_api import *
from server.api.node_api import *
from server.api.stats_api import *
from server.api.tag_api import *
from server.api.scheduler_api import *
from server.api.transactions_api import *
from server.api.packages_api import *
from server.api.api import *
from server.api.virtual import *
from server.api import *
from server.account.manager import AccountManager
from server.oauth.token import TokenManager

from tornado.options import define, options

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

from apscheduler.scheduler import Scheduler
from apscheduler.jobstores.sqlalchemy_store import SQLAlchemyJobStore

define("port", default=9000, help="run on port", type=int)
define("debug", default=True, help="enable debugging features", type=bool)

class HeaderModule(tornado.web.UIModule):
    def render(self):
        return self.render_string(
            "../templates/header.html"
        )

class Application(tornado.web.Application):

    def __init__(self, debug):
        handlers = [
            (r"/?", RootHandler),
            (r"/login/?", LoginHandler),
            (r"/signup/?", CreateUserHandler),
            (r"/logout/?", LogoutHandler),
            (r"/ws/?", WebsocketHandler),
            (r"/test/?", testHandler),
            (r"/developer", DeveloperRegistrationHandler),
            (r"/submitForm", FormHandler),
            (r"/adminForm", AdminHandler),

            #### oAuth 2.0 Handlers
            (r"/login/oauth/authorize/?", AuthorizeHandler),
            (r"/login/oauth/access_token", AccessTokenHandler),

            #### API Handlers
            (r"/api/osData/?", OsHandler),
            (r"/api/networkData/?", NetworkHandler),
            (r"/api/summaryData/?", SummaryHandler),
            #(r"/api/patchData/?", PatchHandler),
            (r"/api/graphData/?", GraphHandler),
            (r"/api/logger/modifyLogging?", LoggingModifyerHandler),
            (r"/api/logger/getParams?", LoggingListerHandler),
            (r"/api/nodes.json/?", NodesHandler),
            (r"/api/patches.json/?", PatchesHandler),
            (r"/api/severity.json/?", SeverityHandler),
            (r"/api/scheduler/list.json/?", SchedulerListerHandler),
            (r"/api/scheduler/add?", SchedulerAddHandler),
            (r"/api/scheduler/remove?", SchedulerRemoveHandler),
            (r"/api/timeblocker/list.json/?", TimeBlockerListerHandler),
            (r"/api/timeblocker/add?", TimeBlockerAddHandler),
            (r"/api/timeblocker/remove?", TimeBlockerRemoverHandler),
            (r"/api/timeblocker/toggler?", TimeBlockerTogglerHandler),
            (r"/api/tagging/listByTag.json/?", TagListerByTagHandler),
            (r"/api/tagging/listByNode.json/?", TagListerByNodeHandler),
            (r"/api/tagging/addTag?", TagAddHandler),
            (r"/api/tagging/addTagPerNode?", TagAddPerNodeHandler),
            (r"/api/tagging/removeTagPerNode?", TagRemovePerNodeHandler),
            (r"/api/tagging/removeTag?", TagRemoveHandler),
            (r"/api/tagging/tagStats?", GetTagStatsHandler),
            (r"/api/transactions/getTransactions?", GetTransactionsHandler),
            (r"/api/package/getDependecies?", GetDependenciesHandler),
            (r"/api/package/searchByPatch?", SearchPatchHandler),
            (r"/api/package/getTagsByTpId?", GetTagsPerTpIdHandler),
            (r"/api/node/modifyDisplayName?", ModifyDisplayNameHandler),
            (r"/api/node/modifyHostName?", ModifyHostNameHandler),
            (r"/api/node/delete?", NodeRemoverHandler),
            (r"/api/node/cleanData?", NodeCleanerHandler),
            (r"/api/ssl/nodeToggler?", NodeTogglerHandler),
            (r"/api/ssl/list.json/?", SslHandler),
            (r"/api/acl/create?", AclModifierHandler),
            (r"/api/acl/modify?", AclModifierHandler),
            (r"/api/acl/delete?", AclModifierHandler),
            (r"/api/userInfo/?", UserHandler),
            (r"/api/users/list?", ListUserHandler),
            (r"/api/users/create?", CreateUserHandler),
            (r"/api/users/delete?", DeleteUserHandler),
            (r"/api/users/toggleGroup?", ModifyUserFromGroupHandler),
            (r"/api/groups/list?", ListGroupHandler),
            (r"/api/groups/create?", CreateGroupHandler),
            (r"/api/groups/delete?", DeleteGroupHandler),
            (r"/api/vmware/snapshots/list?", GetNodeSnapshotsHandler),
            (r"/api/vmware/snapshots/create?", CreateSnapshotHandler),
            (r"/api/vmware/snapshots/revert?", RevertSnapshotHandler),
            (r"/api/vmware/snapshots/remove?", RemoveSnapshotHandler),
            (r"/api/vmware/snapshots/removeAll?", RemoveAllSnapshotsHandler),
            (r"/api/vmware/config/create?", CreateVmwareConfigHandler),
            (r"/api/vmware/config/list?", GetVmwareConfigHandler),
            (r"/api/vendors/?", ApiHandler),                # Returns all vendors
            (r"/api/vendors/?(\w+)/?", ApiHandler),         # Returns vendor with products and respected vulnerabilities.
            (r"/api/vendors/?(\w+)/?(\w+)/?", ApiHandler),  # Returns specific product from respected vendor with vulnerabilities.

            #### File system access whitelist
            (r"/css/(.*?)", tornado.web.StaticFileHandler, {"path": "wwwstatic/css"}),
            (r"/font/(.*?)", tornado.web.StaticFileHandler, {"path": "wwwstatic/font"}),
            (r"/img/(.*?)", tornado.web.StaticFileHandler, {"path": "wwwstatic/img"}),
            (r"/js/(.*?)", tornado.web.StaticFileHandler, {"path": "wwwstatic/js"})
        ]

        template_path = "/opt/TopPatch/tp/templates"
        static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wwwstatic" )
        #ui_modules = { 'Header', HeaderModule }

        settings = {
            "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "login_url": "/login",
        }

        self.db = init_engine()
        Session = create_session(self.db)
        self.session = Session
        self.scheduler = Scheduler()
        self.scheduler.add_jobstore(SQLAlchemyJobStore(engine=self.db, tablename="tp_scheduler"), "toppatch")
        self.scheduler.start()
        self.session = validate_session(self.session)
        self.account_manager = AccountManager(self.session)
        self.tokens = TokenManager(self.session)

        tornado.web.Application.__init__(self, handlers, template_path=template_path, static_path=static_path, debug=debug, **settings)

    def log_request(self, handler):
        logging.config.fileConfig('/opt/TopPatch/tp/src/logger/logging.config')
        log = logging.getLogger('rvweb')
        log_method = log.debug
        if handler.get_status() <= 299:
            log_method = log.info
        elif handler.get_status() <= 399 and \
                handler.get_status() >= 300:
            log_method = log.warn
        elif handler.get_status() <= 499 and \
                handler.get_status() >= 400:
            log_method = log.error
        elif handler.get_status() <= 599 and \
                handler.get_status() >= 500:
            log_method = log.error
        request_time = 1000.0 * handler.request.request_time()
        log_message = '%d %s %.2fms' % (handler.get_status(), handler._request_summary(), request_time)
        log_method(log_message)


class HelloWorldProtocol(Protocol):
    def connectionMade(self):
        SendToSocket("message")

class HelloWorldFactory(Factory):
    protocol = HelloWorldProtocol

class ThreadClass(threading.Thread):
    def run(self):
        reactor.listenTCP(8080, HelloWorldFactory())
        reactor.run(installSignalHandlers=0)



if __name__ == '__main__':
    tornado.options.parse_command_line()
    https_server = tornado.httpserver.HTTPServer(Application(options.debug),
        ssl_options={
            "certfile": os.path.join("/opt/TopPatch/tp/data/ssl/", "server.crt"),
            "keyfile": os.path.join("/opt/TopPatch/tp/data/ssl/", "server.key"),
            })
    https_server.listen(options.port)
    socketListener = ThreadClass()
    socketListener.daemon = True
    socketListener.start()
    tornado.ioloop.IOLoop.instance().start()


