from fastapi import (FastAPI,
                     UploadFile,
                     Depends,
                     status,
                     Body,
                     Request,
                     HTTPException)
import os
from datetime import datetime, timedelta
import shutil
import uuid
from security.main import Token,User
from typing import List
from db.mongo import dbinsert
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from security.main import (authenticate_user,
                           create_access_token,
                           get_current_active_user,
                           hash_pass,add_user)
from security.main  import ACCESS_TOKEN_EXPIRE_MINUTES
from ops.passw import passgen
from ops.main import sshtnl
from ops.multi import MultiOps
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
mg = dbinsert()
obj=sshtnl()
remote = MultiOps()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def start_db():
    await mg.init_db()

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/panel/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/panel/create/")
def user_create(username:str,
                passwd:str,
                current_user: User = Depends(get_current_active_user)):
    try:
        hashpass = hash_pass(passwd)
        add_user(username,hashpass)
        return hashpass
    except:
        return False
    
@app.get("/panel/delete/")
def user_create(username:str,
                current_user: User = Depends(get_current_active_user)):
    try:
        mg.del_user_panel(username)
        return True
    except:
        return False

@app.get("/add-server")
async def add_server(ip_address:str,
                port:int,
                user:str,
                password:str,
                current_user: User = Depends(get_current_active_user)):
    try:
        await mg.add_server(ip_address,port,user,password)
        return True
    except:
        return False
    
@app.get("/list-servers")
async def list_servers(current_user: User = Depends(get_current_active_user)):
    try:
        res = mg.list_servers()
        return res
    except:
        return False

@app.get("/active-user")
def active_user_(server:str,current_user: User = Depends(get_current_active_user)):
    if server == 'localhost':
        local = obj.active_user()
        return local
    else:
        res = remote.all_active_users(server)
        return res

@app.get("/add-user")
async def add_user_(username:str,
              multi:int,
              exdate:str,
              telegram_id:str,
              phone:int,
              server:str,
              email:str | None = '',
              referral:str | None = '',
              traffic:str | None = '',
              desc:str| None = '',
              current_user: User = Depends(get_current_active_user)):
    try:
        passwd=passgen()
        res = await obj.add_user(passwd,username,multi,exdate,telegram_id,phone,email,referral,traffic,desc,server)
        if res == 'user model error':
            return res
        elif res == 'exist':
            return 'exist'
        return {'username':username , 'password':passwd}
    except Exception as e:
        print(e)
        return False



@app.get("/delete-user")
def delete_user_(username:str,server:str,current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            obj.del_user(username)
            return True
        else:
            remote.del_user(server,username)
            return True
    except:
        return False

@app.get("/change-passwd-user")
def change_passwd_user_(mode:str,username:str,server:str,passwd:str | None = '',current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            if mode == 'admin':
                obj.chng_passwd(username,passwd)
                return True
            elif mode == 'users':
                passwdgen=passgen()
                obj.chng_passwd(username,passwdgen)
                return {'username':username , 'password':passwdgen}
        else:
            passwdgen=passgen()
            remote.chng_passwd(server,username,passwdgen)
            return {'username':username , 'password':passwdgen}
    except:
        return False
    
@app.get("/lock-user")
def lock_user_(username:str,server:str,current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            obj.lockuser(username)
            return True
        else:
            remote.lockuser(username,server)
            return True
    except:
        return False

@app.get("/unlock-user")
def unlock_user_(username:str,server:str,current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            obj.unlockuser(username)
            return True
        else:
            remote.unlockuser(username,server)
            return True
    except:
        return False

@app.get("/renew-user")
def renew_user_(username:str,
                 exdate:str,
                 current_user: User = Depends(get_current_active_user)):
    try:
        mg.renew(username,exdate)
        return True
    except:
        return False

@app.get("/get-users")
def get_users_(username:str| None = '',
               current_user: User = Depends(get_current_active_user)):
    if username == 'all':
        try:
            res = mg.select_users()
            return res
        except:
            return False
    else:
        res = mg.select_users()
        for dict in res:
            user = dict['user']
            if user == username:
                    user=dict['user']
                    multi=dict['multi']
                    passwd=dict['passwd']
                    status=dict['status']
                    exdate=dict['exdate']
                    
                    try:
                        telegram_id=dict['telegram_id']
                        phone=dict['phone']
                        email=dict['email']
                        referral=dict['referral']
                        traffic=dict['traffic']
                        desc=dict['desc']
                        server=dict['server']
                    except:
                        telegram_id=''
                        phone=''
                        email=''
                        referral=''
                        traffic=''
                        desc=''
                        server=''
                    
                    return({'user':user,
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

@app.get("/kill-user")
def kill_user_(username:str,server:str,current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            obj.killall(username)
            return True
        else:
            remote.killall(username,server)
            return True
    except:
        return False


@app.post("/user-gen")
async def user_gen(multi:int,exdate:str,count:int,server:str,current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            res = await obj.user_passwd_gen(multi,exdate,count)
            return res
        else:
            res = remote.user_passwd_gen(multi,exdate,count,server)
            return res
    except:
        return False
    
@app.post("/del-kill-users")
async def del_kill_users(items: List[str],mode:str,server:str):
    try:
        if server == 'localhost':
            if mode == 'del':
                for user in items:
                    obj.del_user(user)
                return True
            elif mode == 'kill':
                for user in items:
                    obj.killall(user)
                return True
        else:
            if mode == 'del':
                for user in items:
                    remote.del_user(server,user)
                return True
            elif mode == 'kill':
                for user in items:
                    remote.killall(user,server)
                return True
    except:
        return False
    
@app.get("/search-user")
def search_user(username:str,current_user: User = Depends(get_current_active_user)):
    try:
        res = mg.select_like(username)
        return res
    except:
        return False

@app.get("/change-detail")
def change_detail(username:str,
                   telegram_id:str | None = '',
                   phone:int | None = '',
                   email:str | None = '',
                   traffic:str | None = '',
                   server:str | None = '',
                   current_user: User = Depends(get_current_active_user)):
    try:
        mg.change_detail_user(username,telegram_id,phone,email,traffic,server)
        return True
    except:
        return False
    
@app.get("/change-status")
def change_status(username:str,
                   status:str,
                   server:str | None = '',
                   current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            dict={
                'unlock':obj.unlockuser,
                'lock':obj.lockuser,
            }
            dict.get(status)(username)
            return {'username':username,'status':status}
        else:
            dict_remote={
                'unlock':remote.unlockuser,
                'lock':remote.lockuser,
            }
            dict_remote.get(status)(username)(server)
            return {'username':username,'status':status}
    except Exception as e :
        print(e)
        return False

@app.get("/change-multi")
def change_multi(username:str,
                   multi:int,
                   current_user: User = Depends(get_current_active_user)):
    try:
        mg.update_multi(username,multi)
        return {'username':username,'multi':multi}
    except:
        return False
    
# @app.get("/resource-usage")
# def resource_usage(server:str,current_user: User = Depends(get_current_active_user)):
#     try:
#         if server == 'localhost':
#             res = obj.res_usage()
#             net = obj.network_usage()
#             return res,net
#         else:
#             pass#####ToDo
#     except:
#         return False

# @app.get("/status-clients")
# def status_clients(current_user: User = Depends(get_current_active_user)):
#     try:
#         list = obj.active_user()
#         active = len(list)
#         all_users = mg.select_users()
#         all_users = len(all_users)
#         disable_users = mg.select_disable_user()
#         disable_users = len(disable_users)
#         enable_users = mg.select_enable_user()
#         enable_users = len(enable_users)
#         js = {
#             'all_users':all_users,
#             'active_users': active,
#             'enable_users':enable_users,
#             'disabled_users':disable_users,
#         }
#         return js
#     except:
#         return False