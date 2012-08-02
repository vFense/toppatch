from models.scanner import *

from sqlalchemy.engine import *
from sqlalchemy.orm import *

from datetime import time, date


db = create_engine('mysql://root:topmiamipatch@127.0.0.1/toppatch_server')
Session = sessionmaker(bind=db)
session = Session()


node1 = Node("21.234.345.23", "optimus", True, False)
node2 = Node("21.234.345.22", "megatron", False, False)

meta1 = App("firefox", "1.5.6")
meta2 = App("office", "2010")
meta3 = App("winamp", "5.55")

app = NodeApp(88, "snmp",date.today(), time())
app.node = node1
app.app = meta1

app2 = NodeApp(12, "tcp",date.today(), time())
app2.node = node1
app2.app = meta2

app3 = NodeApp(100, "udc", date.today(), time())
app3.node = node1
app3.app = meta3

session.add(node1)
session.add(node2)

session.add(meta1)
session.add(meta2)
session.add(meta3)

session.add(app)
session.add(app2)
session.add(app3)

session.commit()
