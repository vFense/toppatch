from hashlib import sha512
from uuid import uuid4


def generate_token(length=24):
    return sha512(uuid4().hex).hexdigest()[0:length]