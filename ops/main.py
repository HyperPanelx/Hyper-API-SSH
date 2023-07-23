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
class sshtnl:
    def __init__(self):
        self.mg = dbinsert()
        self.multi = MultiOps()

    def get_user_tun_all(self,user):
        try:
            list=[]
            for dict in self.mg.select_servers() :
                ipaddress=dict['host']
                command="ps aux | grep sshd"
                try:
                    result=self.multi.ssh_main__(command,ipaddress)
                    est = re.findall(f'sshd: ({user}[^\w]*)\n',result)
                    lenuser=(len(est))
                except:
                    pass
                if lenuser > 0:
                    list.append({'username':user,'lenuser':lenuser,'ipaddress':ipaddress})
                lenuser = 0
            result=self.get_user_tun(user)
            if result != 0:
                list.append({'username':user,'lenuser':result,'ipaddress':'localhost',})
            return list
        except:
            False

    def get_user_tun(self,user):
        try:
            string="ps aux | grep sshd"
            result=subprocess.getoutput(string)
            est = re.findall(f'sshd: ({user}[^\w]*)\n',result)
            lenuser=(len(est))
            return lenuser
        except:
            False
        
    def active_user(self):
        try:
            list=[]
            command='ps aux | grep sshd'
            result = subprocess.getoutput(command)
            reg = re.findall('sshd: ([aA-zZ][^\s]*)\n',result)
            for strip in reg:
                if strip != 'root@notty' and strip != 'root' and strip != '[accepted]':
                    list.append(strip)
            return {'localhost':'localhost','users':list}
        except:
            False

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
    
    async def bulk(self,jsname):
        list=[]
        with open('./uploads/'+jsname, 'r',encoding="utf-8") as json_File:
            sample_load_file = load(json_File)
        try:
            for single in sample_load_file:
                passwdgen=passgen()
                username=single['user']
                try:
                    validation= User(
                            user=username,
                            multi=single['multi'],
                            exdate=single['exdate'],
                            telegram_id=single['telegram_id'],
                            phone=0,
                            email='' ,
                            referral='' ,
                            traffic='' ,
                            desc='',
                            passwd=passwdgen,
                            status='enable',
                    )
                    await validation.insert() 
                    self.mg.insert_count_kill(username,'0')
                    list.append({'user':username,'passwd':passwdgen})
                except DuplicateKeyError:
                    # Handle duplicate key error
                    print("Duplicate key value")
                    return 'exist'
                command=f"useradd {username} --shell /usr/sbin/nologin"
                res =subprocess.getoutput(command)
                if res != '':
                    return 'exist'
            return list
        except Exception as e:
            print(e)
    
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