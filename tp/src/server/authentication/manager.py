from models.authentication.account import User, Developer
from server.oauth import token

from utils.security import Crypto

class AccountManager():
    """ AccountManager is a "helper" object to... manage anything and everything with user/developer accounts.

    Stuff it does(tm):
        - create account
        - check if account already exist. i.e if username already exist
        - store newly created account
        - verify password

    Account consist of:
        - username
        - password
        - full name
        - email
    """

    def __init__(self, session):
        self.session = session

    def user_account(self, username, password, fullname=None, email=None):
        """ Create a new account. Returns None if account is not created successfully."""

        # Have to check first if the account with the same username exist.
        account = self.session.query(User).filter(User.username == username).first()
        if account is None:
            hash = Crypto.hash_scrypt(password)

            return User(username, hash)
        else:
            # Looks like a developer account already exist.
            return None

    def dev_account(self, name, redirect_uri=None):
        # Have to check first if the account with the same username exist.
        account = self.session.query(Developer).filter(Developer.name == name).first()
        if account is None:

            client_id = token.generate_token()
            client_secret = token.generate_token()

            return Developer(name, client_id, client_secret, redirect_uri)
        else:
            # Looks like a developer account already exist.
            return None


    def save_account(self, account):

        self.session.add(account)
        self.session.commit()

    def authenticate_account(self, username, password):
        """ Checks if the username and password are correct.
        Returns True if it is, False otherwise.
        """

        account = self.session.query(User).filter(User.username == username).first()
        # Check if account/username exist. False if it doesn't.
        if account is None:
            return False

        if Crypto.verify_scrypt_hash(password, account.hash):
            return True
        else:
            return False

    def authorize_account(self, **permissions):
        """ What the account can and cannot do.
        Implementation forthcoming.
        """
        pass # TODO

    def _account_exist(self, username):
        """ Checks whether an account already exist. Returns True if it does, false otherwise. """

        pass