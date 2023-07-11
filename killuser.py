from ops.main import sshtnl
from ops.multi import MultiOps
import time
from db import dbinsert
mg=dbinsert()
obj=sshtnl()

def kill_user(multi:int):
    count = 0
    while(True):   
        count +=1
        for multiuser in (1,multi):
            print(f'multi = {multiuser} | while = {count}')
            alluserOne=mg.select_user_multi_en(multiuser)
            for username in alluserOne: 
                userlun = obj.get_user_tun(username)
                if userlun > multiuser: # if user tunnel  more than one
                    count_kill=mg.select_count_kill(username)
                    count_kill_update = count_kill + 1
                    mg.update_count_kill(username,count_kill_update)
                    obj.killall(username)
                    print('kill '+username)
                    if count_kill >= 4:
                        # obj.lockuser(username)
                        # print('locked '+username)
                        mg.update_count_kill(username,0)
                        mg.update_status_user(username,'disable')
        time.sleep(120)
kill_user(2)