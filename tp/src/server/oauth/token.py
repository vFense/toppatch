from hashlib import sha512
from uuid import uuid4

class TokenManager():

    def __init__(self, session):
        self.session = session # DB session


    def save_access_token(self, token):
        self.session.add(token)
        self.session.commit()



    def generate_token(self, length=24):
        return sha512(uuid4().hex).hexdigest()[0:length]