import pymongo
import json
from dotenv import load_dotenv
import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Literal
from pydantic import Field
from beanie import Document,init_beanie
from pymongo.errors import DuplicateKeyError
from datetime import datetime
import asyncio
import urllib.parse
from model.userdb import *
import motor.motor_asyncio


load_dotenv()
class dbinsert:
    def __init__(self):
        self.myclient = pymongo.MongoClient(
            os.getenv('MONGO_ADDR'), username=os.getenv('MONGO_USER'), password=os.getenv('MONGO_PASSWD')
        )
        self.urlib = urllib.parse.quote(os.getenv('MONGO_PASSWD'))
        self.mongo_uri = f"mongodb://{os.getenv('MONGO_USER')}:{self.urlib}@{os.getenv('MONGO_ADDR_URI')}"
        self.mydb = self.myclient["dbuser"]
        self.user = self.mydb['user']
        self.user.create_index("user", unique=True)
        self.kill = self.mydb['killer']
        self.api = self.mydb['api']
        self.server = self.mydb['server']

    def select_all_user(self):
        list = []
        for dict in self.user.find():
            list.append(dict)
        return list

    def select_users(self):
        list=[]
        for dict in self.user.find():
            try:
                user=dict['user']
                multi=dict['multi']
                passwd=dict['passwd']
                status=dict['status']
                exdate=dict['exdate']
                server=dict['server']
                try:
                    telegram_id=dict['telegram_id']
                    phone=dict['phone']
                    email=dict['email']
                    referral=dict['referral']
                    traffic=dict['traffic']
                    desc=dict['desc']
                except:
                    telegram_id=''
                    phone=''
                    email=''
                    referral=''
                    traffic=''
                    desc=''
               
                list.append({'user':user,
                            'multi':multi,
                            'exdate':exdate,
                            'telegram_id':telegram_id,
                            'phone':phone,
                            'email':email,
                            'referral':referral,
                            'traffic':traffic,
                            'desc':desc,
                            'passwd':passwd,
                            'status':status,
                            'server':server,
                            }) 
            except:
                pass
        return list 
            
    def user_chng_passwd(self,user,passwd):
        self.user.update_one({"user": user}, {"$set": {"passwd": passwd}})

    def update_user_status(self,user,status):
        self.user.update_one({"user": user}, {"$set": {"status": status}})

    def select_user_multi_en(self,multi_user):
        list = []
        for dict in self.user.find():
            multi = dict['multi']
            user = dict['user']
            status = dict['status']
            if multi == multi_user:
                if status == 'enable':
                    list.append(user)
        return list
    
    def select_disable_user(self):
        list = []
        for dict in self.user.find():
            user = dict['user']
            status = dict['status']
            if status == 'disable':
                list.append(user)
        return list
    
    def select_enable_user(self):
        list = []
        for dict in self.user.find():
            user = dict['user']
            status = dict['status']
            if status == 'enable':
                list.append(user)
        return list
    
    def del_user(self, user):
        self.user.delete_many({"user": user})
        self.kill.delete_many({"username": user})

    def renew(self,user,exdate):
        self.user.update_one({"user": user}, {"$set": {"exdate": exdate}})
    
    def update_multi(self,user,multi):
        self.user.update_one({"user": user}, {"$set": {"multi": multi}})
    
   
    def change_detail_user(self,user,telegram_id,phone,email,traffic):
        self.user.update_one({"user": user}, {"$set": {"telegram_id": telegram_id}})
        self.user.update_one({"user": user}, {"$set": {"phone": phone}})
        self.user.update_one({"user": user}, {"$set": {"email": email}})
        self.user.update_one({"user": user}, {"$set": {"traffic": traffic}})

    def user_mongo(self,user,userhash):
        general = { user: {
        "username": user,
        "full_name": user,
        "hashed_password": userhash,
        }}
        self.api.insert_one(general)

    def del_user_panel(self, user):
        self.api.delete_many({"user": user})

    def select_user_(self):
        list = []
        for dict in self.api.find():
            list.append(dict)
        return list
    
    def insert_count_kill(self,user,count_kill,server):
        general = { 
        "username": user,
        "count_kill": int(count_kill),
        "server":server,
        }
        self.kill.insert_one(general)
    
    def update_count_kill(self,user,count_kill):
        self.kill.update_one({"username": user}, {"$set": {"count_kill": count_kill}})
    
    def select_count_kill(self,user):
        for dict in self.kill.find():
            count_kill = dict['count_kill']
            username = dict['username']
            if username == f'{user}':
                return count_kill

    def update_status_user(self,user,status):
        self.user.update_one({"user": user}, {"$set": {"status": status}})

    
    def select_like(self, user):
        list=[]
        for collect in self.user.find({"user": {"$regex": user}}):
            collect = collect['user']
            list.append(collect)
        return list

    def select_servers(self):
        list = []
        for dict in self.server.find():
            host=dict['host']
            port=dict['port']
            username=dict['username']
            passwd=dict['passwd']
            status=dict['status']
            if status == 'enable':
                js={
                    'host':host,
                    'port':port,
                    'username':username,
                    'passwd':passwd,
                    'status':status,
                    }
                list.append(js)
        return list
    def list_servers(self):
        list = []
        for dict in self.server.find():
            host=dict['host']
            port=dict['port']
            status=dict['status']
            js={
                'host':host,
                'port':port,
                'status':status,
                }
            list.append(js)
        return list
    
    def select_specific_servers(self,server):
        list = []
        for dict in self.server.find():
            host=dict['host']
            port=dict['port']
            username=dict['username']
            passwd=dict['passwd']
            status=dict['status']
            if host == server:
                js={
                    'host':host,
                    'port':port,
                    'username':username,
                    'passwd':passwd,
                    'status':status,
                    }
                list.append(js)
        return list

    
    async def init_db(self):
        client = motor.motor_asyncio.AsyncIOMotorClient(self.mongo_uri)
        await init_beanie(database=client['dbuser'], document_models=[User,Server])
    

    async def add_server(self,hostname,portnum,user,password):
        server = Server(
                host=hostname,
                port=portnum,
                username=user,
                passwd=password,
                status='enable',
        )
        await server.insert() 
    