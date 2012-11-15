from models.base import Base

from sqlalchemy import String, Column, Integer, DateTime, ForeignKey

class AccessToken(Base):
    """ Helper class for an access token.
    http://tools.ietf.org/html/draft-ietf-oauth-v2-30#section-1.4
    """
    __tablename__ = "access_tokens"
    __visit_name__ = "column"
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8'
    }
    id = Column(Integer, primary_key=True)
    token = Column(String(255))
    token_type = Column(String(32)) # Bearer or MAC
    issued_timestamp = Column(DateTime)
    expires = Column(Integer)
    refresh_token = Column(String(255))

    user_id = Column(Integer, ForeignKey('users.id'))
    dev_id = Column(Integer, ForeignKey('developers.id'))


    def __init__(self, token, type, expires, user_id, issue_time, dev_id=None, refresh_token=None):
        self.token = token
        self.token_type = type
        self.issued_timestamp = issue_time
        self.expires = expires
        self.user_id = user_id
        self.dev_id = dev_id
        self.refresh_token = refresh_token
