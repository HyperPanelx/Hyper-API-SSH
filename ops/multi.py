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
    
    def ssh_main__(self,command,server):
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
                            look_for_keys=False,
                            timeout=2 
                            )
                stdin, stdout, stderr = ssh.exec_command(command)
                lines = stdout.read()
                out=lines.decode()
                ssh.close()
                return out
        except:
            False

    def all_active_users(self,mode):
        if mode == 'all':
            list=[]
            for dict in self.mg.select_servers() :
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
            result = self.ssh_main__(command,server)
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
        self.ssh_main__(command,server)

    def lockuser(self,user,server):
        command=f'usermod -L {user}'
        self.ssh_main__(command,server)
        self.mg.update_status_user(user,'disable')
        
    def unlockuser(self,user,server):
        command=f'usermod -U {user}'
        self.ssh_main__(command,server)
        self.mg.update_status_user(user,'enable')

    async def add_user(self,server,passwdgen,username_):
            command=f"useradd {username_} --shell /usr/sbin/nologin ; echo {username_}:{passwdgen} | chpasswd"
            res = self.ssh_main__(command,server)
            reres = re.findall('exists',res)
            if reres == ['exists']:
                print(reres)
                return 'exist'



    def chng_passwd(self,server,user,passwd):
        command=f'echo "{passwd}" | passwd --stdin {user}'
        self.ssh_main__(command,server)
        try:
            self.mg.user_chng_passwd(user,passwd)
        except:
            pass


    def del_user(self,server,user):
        command=f'userdel {user}'
        result=self.ssh_main__(command,server)
        self.mg.del_user(user)


    def res_usage(self,server):
        cpu = "top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'"
        memory_percent="free | awk '/Mem/ {print ($3/$2) * 100}'"
        hdd = "df -h --output=pcent / | awk 'NR==2{print $1}'"
        list = []
        for command in [cpu,memory_percent,hdd]:
            res = self.ssh_main__(command,server)
            list.append(res)
        cpu = list[0].strip()
        mem = list[1].strip()
        hdd = list[2].strip().replace('%','')
        js={'cpu':float(cpu),'mem':float(mem),'hdd':float(hdd)}
        return js

    
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
                res = self.ssh_main__(command)
                if res != '':
                    return 'exist'
            return list
        except Exception as e:
            print(e)
    
    async def user_passwd_gen(self,multi_,exdate_,count_,server_,ordered_by):
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
                            ordered_by=ordered_by,
                    )
                    await validation.insert() 
                    self.mg.insert_count_kill(username,'0',server_)
                    list.append({'user':username,'passwd':passwdgen})
                except DuplicateKeyError:
                    # Handle duplicate key error
                    print("Duplicate key value")
                    return 'exist'
                command=f"useradd {username} --shell /usr/sbin/nologin ; echo {username}:{passwdgen} | chpasswd"
                res = self.ssh_main__(command,server_)
                if res != '':
                    return 'exist'
            return list
        except Exception as e:
            print(e)


    

