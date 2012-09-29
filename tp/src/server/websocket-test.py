__author__ = 'parallels'
import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web


class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print 'new connection'
        self.write_message("Hello World")

    def on_message(self, message):
        print 'message received %s' % message

    def on_close(self):
        print 'connection closed'

    def async_callback(self):
        message = get_installed_patches(operation_id=3456233)
        if message True:
            self.write_message()


application = tornado.web.Application([
    (r'/ws', WSHandler),
])


if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(8000)
    tornado.ioloop.IOLoop.instance().start()


#class WebSocketHandler(BaseHandler, tornado.websocket.WebSocketHandler):
#    def open(self):
#        self.write_message('Connected!')
#
#    def on_message(self, message):
#        self.write_message(message)
#
#    def on_close(self):
#        self.write_mesagge('Close')

