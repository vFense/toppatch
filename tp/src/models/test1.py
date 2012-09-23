from models.base import Base
from models.windows import *
from models.node import *
from sqlalchemy import create_engine

db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
db.echo = True
from sqlalchemy.orm import sessionmaker
import datetime
Session = sessionmaker(bind=db)
session = Session()
u1 = NodeInfo("192.168.1.1", "test1.com", "windows", "Windows 7", None, None, None, None, True, True, datetime.datetime.now(), datetime.datetime.now() )
u2 = NodeInfo("192.168.1.2", "test2.com", "windows", "Windows XP", None, None, None, "SP3", True, True, datetime.datetime.now(), datetime.datetime.now() )
session.add(u1)
session.add(u2)
session.commit()
n1 = Operations(1, None, "install", datetime.datetime.now(), None)
session.add(n1)
w1 = WindowsUpdate("20120901", "Mozilla", "FireFox 15", "2nd best browser", "http://firefox.com", 'Critical', datetime.date(month=9, year=2012, day=1))
session.add(w1)
a = session.query(NodeInfo.id).filter_by(host_name="test1.com").first()
b = session.query(Operations.id).filter_by(node_id=a.id).first()
c = session.query(WindowsUpdate.toppatch_id).filter_by(title="Firefox 15").first()
r1 = Results(a.id, b.id, c.toppatch_id, True, None)
session.add(r1)
#o1 =  session.query(Operations).filter_by(node_id=a.id).first()
#session.execute(o1.__table__.update().values(operation_received=datetime.datetime.now(), results_id=r1.id))
o1 =  session.query(Operations).filter_by(node_id=a.id).update({'operation_received' : datetime.datetime.now()}
session.commit()

