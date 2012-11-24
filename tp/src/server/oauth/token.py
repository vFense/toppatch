from hashlib import sha512
from uuid import uuid4
from db.client import validateSession

class TokenManager():

    def __init__(self, session):
        self.session = session # DB session

    def save_access_token(self, token):
        self.session = validateSession(self.session)
        self.session.add(token)
        self.session.commit()
        self.session.close()



    def generate_token(self, length=24):
        return sha512(uuid4().hex).hexdigest()[0:length]
