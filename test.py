from db.mongo import dbinsert
import traceback
from ops.multi import MultiOps
obj=MultiOps()
mg = dbinsert()
for dict in mg.select_servers():
    ipaddress=dict['host']
    port=dict['port']
    username=dict['username']
    passwd=dict['passwd']
