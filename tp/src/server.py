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

from server.handlers import RootHandler, LoginHandler, SignupHandler, LogoutHandler
from server.oauth.handlers import AuthorizeHandler, TokenHandler

from server.api import *
from server.authentication.manager import AccountManager

from tornado.options import define, options
define("port", default=8000, help="run on port", type=int)
define("debug", default=True, help="enable debugging features", type=bool)

class Application(tornado.web.Application):

    def __init__(self, debug):
        handlers = [

            (r"/?", RootHandler),
            (r"/login/?", LoginHandler),
            (r"/signup/?", SignupHandler),
            (r"/logout/?", LogoutHandler),

            #### oAuth 2.0 Handlers
            (r"/login/oauth/authorize/?", AuthorizeHandler),
            (r"/login/oauth/access_token", TokenHandler),


            #### API Handlers
            (r"/api/vendors/?", ApiHandler),                # Returns all vendors
            (r"/api/vendors/?(\w+)/?", ApiHandler),         # Returns vendor with products and respected vulnerabilities.
            (r"/api/vendors/?(\w+)/?(\w+)/?", ApiHandler)]  # Returns specific product from respected vendor with vulnerabilities.

        settings = {
            "cookie_secret": base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            "login_url": "/login",
            }

        self.db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')

        Session = sessionmaker(bind=self.db)
        self.session = Session()
        self.account_manager = AccountManager(self.session)

        tornado.web.Application.__init__(self, handlers, debug=debug, **settings)



if __name__ == '__main__':
    tornado.options.parse_command_line()
    https_server = tornado.httpserver.HTTPServer(Application(options.debug),
        ssl_options={
            "certfile": os.path.join("data/ssl", "server.crt"),
            "keyfile": os.path.join("data/ssl", "server.key"),
            })
    https_server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()