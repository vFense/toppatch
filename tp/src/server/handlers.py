
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
        self.write("Hello, " + name)

class LoginHandler(BaseHandler):
    def get(self):
        self.write('<html>'
                    '<body>'
                        '<form action="/login" method="post">'
                        'Name: <input type="text" name="name">'
                        'Password: <input type="password" name="password">'
                        '<input type="submit" value="Sign in">'
                        '</form>'
                    '</body></html>')

    def post(self):

        self._save_user()

        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")

    def _save_user(self):

        name = self.get_argument("name")
        password = str(self.get_argument("password"))

        hash = Crypto.hash_scrypt(password)
        account = Account(name, hash)

        self.application.session.add(account)
        self.application.session.commit()