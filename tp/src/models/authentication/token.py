from models.base import Base

from sqlalchemy import String, Column, Integer, DateTime

class AccessToken(Base):
    """ Helper class for an access token.
    http://tools.ietf.org/html/draft-ietf-oauth-v2-30#section-1.4
    """
    __tablename__ = "access_tokens"

    id = Column(Integer, primary_key=True)
    token = Column(String(255))
    token_type = Column(String(32)) # Bearer or MAC
    issued_timestamp = Column(DateTime)
    expires = Column(Integer)

    def __init__(self, token, type, timestamp, expires):
        self.token = token
        self.token_type = type
        self.issued_timestamp = timestamp
        self.expires = expires