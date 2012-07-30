import functools
import urllib
import urlparse

from tornado.web import HTTPError

def authenticated_request(method):
    """ Decorator that handles authenticating the request. Be it either by access tokens for third-party access or by
    secure cookies. In the spirit of the tornado.web.authenticated decorator.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):

        # Get the access token argument. If nothing is provided, string will be "Invalid"
        # Chose this way instead of using "try" and catching HttpError 400 which get_argument throws
        access_token = str(self.get_argument("access_token", default="Invalid"))


        # Check if an access token is legit.
        if access_token is not "Invalid":
            print "1st if"

            return method(self, *args, **kwargs)

        # If the access token is not provided, assumes is the main ui client.
        if not self.current_user:
            print "2nd if"
            if self.request.method in ("GET", "HEAD"):
                url = self.get_login_url()
                if "?" not in url:
                    if urlparse.urlsplit(url).scheme:
                        # if login url is absolute, make next absolute too
                        next_url = self.request.full_url()
                    else:
                        next_url = self.request.uri
                    url += "?" + urllib.urlencode(dict(next=next_url))
                self.redirect(url)
                return
            raise HTTPError(403)

        return method(self, *args, **kwargs)

    return wrapper