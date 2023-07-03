import paramiko
from db import dbinsert
import re
from model.userdb import User
import psutil
from json import load
from ops.passw import passgen
from names_generator import generate_name
import time
from pymongo.errors import DuplicateKeyError
import traceback

class MultiOps:
    def __init__(self):
        self.mg = dbinsert()
    
    def __ssh_main(self,command,server):
        res = self.mg.select_specific_servers(server)
        for dict in res:
            ipaddress=dict['host']
            port=dict['port']
            username=dict['username']
            passwd=dict['passwd']
        try:
            with paramiko.SSHClient() as ssh:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(ipaddress,
                            port,
                            username,
                            passwd,
                            allow_agent=False,
                            look_for_keys=False
                            )
                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.read()
                out=lines.decode()
                ssh.close()
                return out
        except:
            False

    def get_user_tun(self,user):
        try:
            command="ps aux | grep sshd"
            result=self.__ssh_main(command)
            est = re.findall(f'sshd: ({user}[^\w]*)\n',result)
            lenuser=(len(est))
            return lenuser
        except:
            False

    def all_active_users(self,mode):
        if mode == 'all':
            list=[]
            for dict in self.mg.select_servers():
                ipaddress=dict['host']
                # username=dict['username']
                res=self.active_user(ipaddress)
                
                list.append({'ip-address':ipaddress,'users':res})
            return list
        else:
            res=self.active_user(mode)
            return({'ip-address':mode,'users':res})
    

    def active_user(self,server):
        try:
            list=[]
            command='ps aux | grep sshd'
            result = self.__ssh_main(command,server)
            reg = re.findall('sshd: ([aA-zZ][^\s]*)\n',result)
            for strip in reg:
                if strip != 'root@notty' and strip != 'root' and strip != '[accepted]': 
                    list.append(strip)
            return list
        except Exception:
            print(traceback.format_exc())
            False

    def killall(self,user,server):            
        command=f"killall -u {user}"
        self.__ssh_main(command,server)

    def lockuser(self,user,server):
        command=f'usermod -L {user}'
        self.__ssh_main(command,server)
        self.mg.update_status_user(user,'disable')
        
    def unlockuser(self,user,server):
        command=f'usermod -U {user}'
        self.__ssh_main(command,server)
        self.mg.update_status_user(user,'enable')

    async def add_user(self,server,passwdgen,username_):
            command=f"useradd {username_} --shell /usr/sbin/nologin ; echo {username_}:{passwdgen} | chpasswd"
            res = self.__ssh_main(command,server)
            reres = re.findall('exists',res)
            if reres == ['exists']:
                print(reres)
                return 'exist'



    def chng_passwd(self,server,user,passwd):
        command=f'echo "{passwd}" | passwd --stdin {user}'
        self.__ssh_main(command,server)
        try:
            self.mg.user_chng_passwd(user,passwd)
        except:
            pass


    def del_user(self,server,user):
        command=f'userdel {user}'
        result=self.__ssh_main(command,server)
        self.mg.del_user(user)


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
                res = self.__ssh_main(command)
                if res != '':
                    return 'exist'
            return list
        except Exception as e:
            print(e)
    
    async def user_passwd_gen(self,multi_,exdate_,count_,server_):
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
                            server=server_,
                    )
                    await validation.insert() 
                    self.mg.insert_count_kill(username,'0',server_)
                    list.append({'user':username,'passwd':passwdgen})
                except DuplicateKeyError:
                    # Handle duplicate key error
                    print("Duplicate key value")
                    return 'exist'
                command=f"useradd {username} --shell /usr/sbin/nologin ; echo {username}:{passwdgen} | chpasswd"
                res = self.__ssh_main(command,server_)
                if res != '':
                    return 'exist'
            return list
        except Exception as e:
            print(e)


    

