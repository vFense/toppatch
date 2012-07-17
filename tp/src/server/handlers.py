
import tornado.web

from models.auth.account import Account

from utils.security import Crypto

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
            self.set_secure_cookie("user", self.get_argument("name"))
            self.redirect("/")
         else:
             self.write("Invalid username and/or password .")

#    def _authenticate_user(self):
#
#        name = self.get_argument("name")
#        password = str(self.get_argument("password"))
#
#        account = self.application.session.query(Account).filter(Account.name == name).first()
#
#        if account is None:
#            return False
#
#        if Crypto.verify_scrypt_hash(password, account.hash):
#            return True
#        else:
#            return False



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

        if self.application.account_manager.create_account(str(self.get_argument("name")), str(self.get_argument("password"))):

            self.set_secure_cookie("user", self.get_argument("name"))
            self.redirect("/")
        else:
            self.write("Username already exist.")

class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        self.write("Goodbye!" + '<br><a href="/login">Login</a>')