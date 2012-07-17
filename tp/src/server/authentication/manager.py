from models.auth.account import Account

from utils.security import Crypto

class AccountManager():
    """ AccountManager is a "helper" object to... manage anything and everything with accounts.

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

    def create_account(self, username, password, fullname=None, email=None):
        """ Create a new account and save it to the database. Returns false if account is not created successfully."""

        # Have to check first if the account with the same username exist.
        account = self.session.query(Account).filter(Account.username == username).first()
        if account is None:
            hash = Crypto.hash_scrypt(password)

            # Add new account to database and finish transactions.
            account = Account(username, hash)
            self.session.add(account)
            self.session.commit()
            return True
        else:
            return False

    def _save_account(self, username, password, full_name, email=None):
        pass

    def authenticate_account(self, username, password):
        """ Checks if the username and password are correct.
        Returns True if it is, False otherwise.
        """

        account = self.session.query(Account).filter(Account.username == username).first()
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
        pass

    def _account_exist(self, username):
        """ Checks whether an account already exist. Returns True if it does, false otherwise. """

        pass