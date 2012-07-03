"""
Main launching point of the Top Patch Server
"""
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options

from sqlalchemy.engine import *
from sqlalchemy.orm import *

from server.api import *

from tornado.options import define, options
define("port", default=8000, help="run on port", type=int)
define("debug", default=True, help="enable debugging features", type=bool)

class Application(tornado.web.Application):

    def __init__(self, debug):
        handlers = [


            #### API Handlers
            (r"/api/vendors/?", ApiHandler),
            (r"/api/vendors/?(\w+)", ApiHandler)]

        self.db = create_engine('mysql://root:topmiamipatch@127.0.0.1/vuls')

        Session = sessionmaker(bind=self.db)
        self.session = Session()

        tornado.web.Application.__init__(self, handlers, debug=debug)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(options.debug))
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()