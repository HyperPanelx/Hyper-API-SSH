from ops.main import sshtnl
from ops.multi import MultiOps
import time
from db import dbinsert
mg=dbinsert()
obj=sshtnl()
remote=MultiOps()
def kill_user(multi:int):
    count = 0
    while(True):   
        count +=1
        for multiuser in (1,multi):
            print(f'multi = {multiuser} | while = {count}')
            alluserOne=mg.select_user_multi_en(multiuser)
            for username in alluserOne: 
                try:
                    usertun = obj.get_user_tun_all(username)
                    for dict in usertun:
                        username = dict['username']
                        ipaddress = dict['ipaddress']
                        usertun = dict['lenuser']
                    if usertun > multiuser:
                        count_kill=mg.select_count_kill(username)
                        count_kill_update = count_kill + 1
                        mg.update_count_kill(username,count_kill_update)
                        if ipaddress == 'localhost':
                            obj.killall(username)
                            print(f'kill {username}')
                        else:
                            remote.killall(username,ipaddress)
                            print(f'kill {username}')
                        if count_kill >= 4:
                            if ipaddress == 'localhost':
                                obj.lockuser(username)
                                print('locked '+username)
                            else:
                                remote.lockuser(username,ipaddress)
                                print(f'lock {username}')
                            mg.update_count_kill(username,0)
                            mg.update_status_user(username,'disable')
                except:
                    pass
        time.sleep(60)
kill_user(2)
