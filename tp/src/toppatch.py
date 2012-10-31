"""
Main launching point of the Top Patch Server
"""
import base64
import uuid
import os

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

from sqlalchemy.engine import *
from sqlalchemy.orm import *

from server.handlers import RootHandler, LoginHandler, SignupHandler, WebsocketHandler, testHandler, LogoutHandler, DeveloperRegistrationHandler, FormHandler, AdminHandler
from server.oauth.handlers import AuthorizeHandler, AccessTokenHandler

from server.api import *
from server.account.manager import AccountManager
from server.oauth.token import TokenManager

from tornado.options import define, options

define("port", default=8000, help="run on port", type=int)
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
            (r"/signup/?", SignupHandler),
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
            (r"/api/nodeData/?", NodeHandler),
            (r"/api/osData/?", OsHandler),
            (r"/api/networkData/?", NetworkHandler),
            (r"/api/summaryData/?", SummaryHandler),
            (r"/api/patchData/?", PatchHandler),
            (r"/api/graphData/?", GraphHandler),
            (r"/api/nodes.json/?", NodesHandler),
            (r"/api/patches.json/?", PatchesHandler),
            (r"/api/severity.json/?", SeverityHandler),
            (r"/api/csrinfo.json/?", CsrHandler),
            (r"/api/userInfo/?", UserHandler),
            (r"/api/vendors/?", ApiHandler),                # Returns all vendors
            (r"/api/vendors/?(\w+)/?", ApiHandler),         # Returns vendor with products and respected vulnerabilities.
            (r"/api/vendors/?(\w+)/?(\w+)/?", ApiHandler),  # Returns specific product from respected vendor with vulnerabilities.

            #### File system access whitelist
            (r"/css/(.*?)", tornado.web.StaticFileHandler, {"path": "../wwwstatic/css"}),
            (r"/font/(.*?)", tornado.web.StaticFileHandler, {"path": "../wwwstatic/font"}),
            (r"/img/(.*?)", tornado.web.StaticFileHandler, {"path": "../wwwstatic/img"}),
            (r"/js/(.*?)", tornado.web.StaticFileHandler, {"path": "../wwwstatic/js"})
        ]

        template_path = "/opt/TopPatch/tp/templates"
        static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wwwstatic" )
        #ui_modules = { 'Header', HeaderModule }

        settings = {
            "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "login_url": "/login",
        }

        self.db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')

        Session = sessionmaker(bind=self.db)
        self.session = Session()
        self.account_manager = AccountManager(self.session)
        self.tokens = TokenManager(self.session)

        tornado.web.Application.__init__(self, handlers, template_path=template_path, static_path=static_path, debug=debug, **settings)

"""
class HelloWorldProtocol(Protocol):
    def connectionMade(self, msg):
        SendToSocket(msg)

class HelloWorldFactory(Factory):
    protocol = HelloWorldProtocol

class ThreadClass(threading.Thread):
    def run(self):
        reactor.listenTCP(8080, HelloWorldFactory())
        #reactor.run()
        reactor.run(installSignalHandlers=0)
"""

if __name__ == '__main__':
    tornado.options.parse_command_line()
    https_server = tornado.httpserver.HTTPServer(Application(options.debug),
        ssl_options={
            "certfile": os.path.join("/opt/TopPatch/tp/data/ssl/", "server.crt"),
            "keyfile": os.path.join("/opt/TopPatch/tp/data/ssl/", "server.key"),
            })
    https_server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()


