import re
import time
from db import dbinsert
import subprocess
from model.models import User
import psutil
from json import load
from ops.passwd import passgen
from names_generator import generate_name
from pymongo.errors import DuplicateKeyError
from .multi import MultiOps
import traceback
from collections import Counter
class sshtnl:
    def __init__(self):
        self.mg = dbinsert()
        self.multi = MultiOps()

    def get_user_tun_all(self,user):
        try:
            list=[]
            for dict in self.mg.select_servers() :
                ipaddress=dict['host']
                command=f"lsof -i -n | egrep '\<ssh\>' | grep {user}"
                try:
                    result=self.multi.ssh_main__(command,ipaddress)
                    pattern =  r'ssh->(\b(?:\d{1,3}\.){3}\d{1,3}\b)'
                    est = re.findall(pattern,result)
                    counts = Counter(est)
                    list_count=[]
                    for dict_count in counts:
                            list_count.append(dict_count)
                    lenuser=(len(list_count))
                    if lenuser > 0:
                        list.append({'username':user,'lenuser':lenuser,'ipaddress':ipaddress,'client_ip':est})
                except:
                    pass
            result=self.get_user_tun(user)
            local_len_user=(len(result))
            list.append({'username':user,'lenuser':local_len_user,'ipaddress':'localhost','client_ip':result})
            return list
           
        except Exception:
            print(traceback.format_exc())
            False

    def get_user_tun(self,user):
        try:
            command=f"lsof -i -n | egrep '\<ssh\>' | grep {user}"
            result=subprocess.getoutput(command)
            pattern =  r'ssh->(\b(?:\d{1,3}\.){3}\d{1,3}\b)'
            est = re.findall(pattern,result)
            counts = Counter(est)
            list_count=[]
            for dict_count in counts:
                    list_count.append(dict_count)
            return list_count
        except:
            False
        
    def active_user(self):
        try:
            list=[]
            command='ps aux | grep sshd'
            result = subprocess.getoutput(command)
            reg = re.findall('sshd: ([aA-zZ][^\s]*)\n',result)
            for strip in reg:
                if strip != 'root@notty' and strip != 'root' and strip != '[accepted]'and strip != '[net]':
                    list.append(strip)
            counts = Counter(list)
            return {'localhost':'localhost','users':counts}
        except:
            False

    def all_active_users(self,mode):
        if mode == 'all':
            list=[]
            for dict in self.mg.select_servers() :
                ipaddress=dict['host']
                res=self.multi.active_user(ipaddress)
                if res == False:
                    res = 'Server is Down'
                list.append({'ip-address':ipaddress,'users':res})
            local=self.active_user()
            list.append(local)
            return list
        else:
            res=self.multi.active_user(mode)
            return({'ip-address':mode,'users':res})
        
    def killall(self,user):            
        command=f"killall -u {user}"
        subprocess.getoutput(command)

    def lockuser(self,user):
        command=f'usermod -L {user}'
        subprocess.getoutput(command)
        self.mg.update_status_user(user,'disable')
        
    def unlockuser(self,user):
        command=f'usermod -U {user}'
        subprocess.getoutput(command)
        self.mg.update_status_user(user,'enable')

    async def add_user(self,passwdgen,
                       username_,
                       multi_,
                       exdate_,
                       telegram_id_,
                       phone_,
                       email_,
                       referral_,
                       traffic_,
                       desc_,
                       server,
                       ordered_by_):
            try:
                user_model = User(
                    user=username_,
                    multi=multi_,
                    exdate=exdate_,
                    telegram_id=telegram_id_,
                    phone=phone_,
                    email=email_ ,
                    referral=referral_ ,
                    traffic=traffic_ ,
                    desc=desc_,
                    passwd=passwdgen,
                    status='enable',
                    server=server,
                    ordered_by=ordered_by_,
                )
                await user_model.insert()  
                self.mg.insert_count_kill(username_,'0',server)
               
            except DuplicateKeyError:
                # Handle duplicate key error
                print("Duplicate key value")
                return 'exist'
            if server == 'localhost':
                command=f"useradd {username_} --shell /usr/sbin/nologin ; echo {username_}:{passwdgen} | chpasswd"
                res =subprocess.getoutput(command)
                reres = re.findall('exists',res)
                if reres == ['exists']:
                    print(reres)
                    return 'exist'
            else:
                self.multi.add_user(server,passwdgen,username_)



    def chng_passwd(self,user,passwd):
        command=f'echo "{passwd}" | passwd --stdin {user}'
        subprocess.getoutput(command)
        try:
            self.mg.user_chng_passwd(user,passwd)
        except:
            pass


    def del_user(self,user):
        command=f'userdel {user}'
        result=subprocess.getoutput(command)
        self.mg.del_user(user)

    def ops_cm(self,command):
        result=subprocess.getoutput(command)
        return result

    def res_usage(self):
        cpu = psutil.cpu_percent(4)
        mem = psutil.virtual_memory()[2]
        hdd = psutil.disk_usage('/')[3]
        return {'cpu':cpu,'mem':mem,'hdd':hdd}

    def get_size(self,bytes):
        """
        Returns size of bytes in a nice format
        """
        for unit in ['', 'K', 'M', 'G', 'T', 'P']:
            if bytes < 1024:
                return f"{bytes:.2f}{unit}B"
            bytes /= 1024

    def network_usage(self):
        UPDATE_DELAY = 1 
        io = psutil.net_io_counters()
        bytes_sent, bytes_recv = io.bytes_sent, io.bytes_recv
        while True:
            time.sleep(UPDATE_DELAY)
            io_2 = psutil.net_io_counters()
            us, ds = io_2.bytes_sent - bytes_sent, io_2.bytes_recv - bytes_recv
            return {'Upload': self.get_size(io_2.bytes_sent)   ,
                'Download': self.get_size(io_2.bytes_recv)  ,
                'Upload Speed': self.get_size(us / UPDATE_DELAY),
                'Download Speed': self.get_size(ds / UPDATE_DELAY)}
    
    async def user_passwd_gen(self,multi_,exdate_,count_,server_,ordered_by_,server):
        list=[]
        try:
            for single in range(0,count_):
                username=generate_name()
                passwdgen=passgen()
                try:
                    validation= User(
                            user=username,
                            multi=multi_,
                            exdate=exdate_,
                            telegram_id='',
                            phone=0,
                            email='' ,
                            referral='' ,
                            traffic='' ,
                            desc='',
                            passwd=passwdgen,
                            status='enable',
                            server = server_,
                            ordered_by=ordered_by_,
                    )
                    await validation.insert() 
                    self.mg.insert_count_kill(username,'0',server)
                    list.append({'user':username,'passwd':passwdgen})
                except DuplicateKeyError:
                    # Handle duplicate key error
                    print("Duplicate key value")
                    return 'exist'
                command=f"useradd {username} --shell /usr/sbin/nologin ; echo {username}:{passwdgen} | chpasswd"
                res =subprocess.getoutput(command)
                if res != '':
                    return 'exist'
            return list
        except Exception as e:
            print(e)