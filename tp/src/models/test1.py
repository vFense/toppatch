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
u1 = NodeInfo("192.168.1.1", "test1.com", True, True, datetime.datetime.now(), datetime.datetime.now(), True )
u2 = NodeInfo("192.168.1.2", "test2.com", True, True, datetime.datetime.now(), datetime.datetime.now(), False )
u3 = NodeInfo("192.168.1.3", "test3.com", True, True, datetime.datetime.now(), datetime.datetime.now(), False )
session.add(u1)
session.add(u2)
session.add(u3)
session.commit()
s1 = SystemInfo(2, 'Windows', 'Windows Server (R) 2008 Datacenter', '32', None, None, None, 'SP3')
s2 = SystemInfo(1, 'Windows', 'Windows Server 2008 (R2) Datacenter', '64', None, None, None, 'SP1')
s3 = SystemInfo(3, 'Linux', 'Ubuntu', '', None, None, None, '12.04')
session.add(s1)
session.add(s2)
session.add(s3)
session.commit()
n1 = Operations(1, "install", None, datetime.datetime.now(), None)
session.add(n1)
w0 = WindowsUpdate("20120902", "kb989024", "Chrome", "Chrome 20", "1st best browser", "http://google.chrome.com", "Critical", datetime.date(month=9, year=2012, day=1), 300)
w1 = WindowsUpdate("20120901", "kb989025", "Mozilla", "FireFox 15", "2nd best browser", "http://firefox.com", 'Critical', datetime.date(month=9, year=2012, day=1), 500)
w2 = WindowsUpdate("20120903", "kb989026", "Windows", "Windows Security 1", "security patch", "http://google.chrome.com", "Optional", datetime.date(month=9, year=2012, day=1), 300)
w3 = WindowsUpdate("20120904", "kb989027", "Windows", "Windows Security 2", "security patch", "http://firefox.com", 'Important', datetime.date(month=9, year=2012, day=1), 500)

session.add(w0)
session.add(w1)
session.add(w2)
session.add(w3)
session.commit()
x0 = ManagedWindowsUpdate(1, '20120903', datetime.datetime.now(), False, False, 2, False)
x1 = ManagedWindowsUpdate(1, '20120904', datetime.datetime.now(), False, False, 3, True)
x2 = ManagedWindowsUpdate(1, '20120901', datetime.datetime.now(), False, False, 1, True) #hidden,  installed,  attempts,  pending
x3 = ManagedWindowsUpdate(1, '20120902', datetime.datetime.now(), False, True, 1, False)


x4 = ManagedWindowsUpdate(2, '20120901', datetime.datetime.now(), False, True, 1, False)
x5 = ManagedWindowsUpdate(2, '20120902', datetime.datetime.now(), False, True, 1, False)
x6 = ManagedWindowsUpdate(2, '20120903', datetime.datetime.now(), False, True, 4, False)
x7 = ManagedWindowsUpdate(2, '20120904', datetime.datetime.now(), False, False, 2, False)

x8 = ManagedWindowsUpdate(3, '20120901', datetime.datetime.now(), False, False, 0, True)
x9 = ManagedWindowsUpdate(3, '20120902', datetime.datetime.now(), False, False, 0, False)
x10 = ManagedWindowsUpdate(3, '20120903', datetime.datetime.now(), False, False, 1, False)
x11 = ManagedWindowsUpdate(3, '20120904', datetime.datetime.now(), False, False, 1, True)

session.add(x0)
session.add(x1)
session.add(x2)
session.add(x3)
session.add(x4)
session.add(x5)
session.add(x6)
session.add(x7)
session.add(x8)
session.add(x9)
session.add(x10)
session.add(x11)

n0 = NodeStats(1, 1, 1, 2, 1) #node_id, patches_installed, patches_available, patches_pending, patches_failed
n1 = NodeStats(2, 3, 1, 0, 1)
n2 = NodeStats(3, 0, 2, 2, 1)
session.add(n0)
session.add(n1)
session.add(n2)
g0 = NetworkStats(4, 4, 4, 3) #installed, available, pending, failed
session.add(g0)
a = session.query(NodeInfo.id).filter_by(host_name="test1.com").first()
b = session.query(Operations.id).filter_by(node_id=a.id).first()
c = session.query(WindowsUpdate.toppatch_id).filter_by(title="Firefox 15").first()
r1 = Results(a.id, b.id, c.toppatch_id, True, None)
session.add(r1)
o1 =  session.query(Operations).filter_by(node_id=a.id).first()
session.execute(o1.__table__.update().values(operation_received=datetime.datetime.now(), results_id=r1.id))
o1 =  session.query(Operations).filter_by(node_id=a.id).update({'operation_received' : datetime.datetime.now()})
session.commit()
