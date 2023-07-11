import time
from ops.main import sshtnl
from db.mongo import dbinsert
mg=dbinsert()
main=sshtnl()
def exdate(datet,user):
    class Timedelta(object):
        @property
        def isoformat(self):
            return str()
    ExpirationDate = time.strftime("%Y-%m-%d")
    if ExpirationDate > datet:
        main.lockuser(user)
    else:
        pass
selc=mg.select_all_user()
for dict in selc:
    user=dict['user']
    exdate_user=dict['exdate']
    exdate(exdate_user,user)
