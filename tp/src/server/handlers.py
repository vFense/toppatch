
import tornado.web
import tornado.websocket
from models.node import NodeInfo
from server.decorators import authenticated_request


def printToSocket(fn):
    def wrapped():
        if WebsocketHandler.socket:
            return WebsocketHandler.socket.write_message(fn())
        else:
            print fn()
    return wrapped

class BaseHandler(tornado.web.RequestHandler):

    def get_current_user(self):
        #self.clear_all_cookies()
        return self.get_secure_cookie("user")

class RootHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        name = tornado.escape.xhtml_escape(self.current_user)
        self.write("Hello, " + name + '<br><a href="/logout">Logout</a>')


class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html>'
                    '<body>'
                        '<form action="/login" method="post">'
                        'Name: <input type="text" name="name">'
                        'Password: <input type="password" name="password">'
                        '<input type="submit" value="Sign in">'
                        '</form>'
                        '<a href="/signup">Create Account</a>'
                    '</body></html>')

    def post(self):

         if self.application.account_manager.authenticate_account(str(self.get_argument("name")), str(self.get_argument("password"))):
            @printToSocket
            def sign():
                return '{ "user": "%s", "status": "signed in" }' % self.get_argument('name')
            sign()
            self.set_secure_cookie("user", self.get_argument("name"))
            self.redirect("/")
         else:
             self.write("Invalid username and/or password .")



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

        user = self.application.account_manager.user_account(str(self.get_argument("name")), str(self.get_argument("password")))

        if user is not None:
            self.application.account_manager.save_account(user)
            self.set_secure_cookie("user", self.get_argument("name"))
            self.redirect("/")
        else:
            self.write("Username already exist.")

class testHandler(BaseHandler):
    def get(self):
        self.render('../data/templates/websocket-test.html')

class WebsocketHandler(BaseHandler, tornado.websocket.WebSocketHandler):

    socket = ""
    @authenticated_request
    def open(self):
        print 'new connection'
        global socket
        WebsocketHandler.socket = self

    def on_message(self, message):
        print 'message received %s' % message

    def on_close(self):
        print 'connection closed...'
        WebsocketHandler.socket = ""

    def callback(self):
        self.write_message(globalMessage)

class LogoutHandler(BaseHandler):
    def get(self):
        @printToSocket
        def sign():
            return '{ "user": "%s", "status": "logged out" }' % self.current_user
        sign()
        WebsocketHandler.socket.close()
        self.clear_all_cookies()
        self.write("Goodbye!" + '<br><a href="/login">Login</a>')

class DeveloperRegistrationHandler(BaseHandler):
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


