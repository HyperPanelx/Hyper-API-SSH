from fastapi import (FastAPI,
                     Depends,
                     Response,
                     APIRouter)
from security.main import User
from security.main import *
from ops.multi import MultiOps
from ops.main import sshtnl
from ops.multi import MultiOps
from db.mongo import dbinsert
from ops.passwd import passgen
from typing import List

remote = MultiOps()
mg = dbinsert()
obj = sshtnl()
router = APIRouter(tags=['Users'])
@router.get("/user-add")
async def add_user_(response: Response,
                username:str,
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
        ordered_by=current_user.username
        passwd = passgen()
        res = await obj.add_user(passwd,username,multi,exdate,telegram_id,phone,email,referral,traffic,desc,server,ordered_by)
        if res == 'user model error':
            return {"success":True,"message": "OK","data":res}
        elif res == 'exist':
            return {"success":False,"message": "faild","data":"exist"}
        response.status_code = 200
        return {"success":True,"message": "OK","data":{'username':username , 'password':passwd}}
    
    except Exception as e:
        print(e)
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}



@router.get("/user-delete", dependencies=[Depends(has_permission)])
def delete_user_(response: Response,username:str,server:str,current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            obj.del_user(username)
            response.status_code = 200
            return {"success":True,"message": "OK","data":""}
        else:
            remote.del_user(server,username)
            response.status_code = 200
            return {"success":True,"message": "OK","data":""}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}

@router.get("/user-change-passwd", dependencies=[Depends(has_permission)])
def change_passwd_user_(response: Response,
                        mode:str,
                        username:str,
                        server:str,
                        passwd:str | None = '',
                        current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            if mode == 'admin':
                obj.chng_passwd(username,passwd)
                response.status_code = 200
                return {"success":True,"message": "OK","data":""}
            elif mode == 'users':
                obj.chng_passwd(username,passwd)
                response.status_code = 200
                return {'username':username , 'password':passwd}
        else:
            remote.chng_passwd(server,username,passwd)
            response.status_code = 200
            return {'username':username , 'password':passwd}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}
    
@router.get("/user-renew")
def renew_user_(response: Response,
                username:str,
                exdate:str,
                current_user: User = Depends(get_current_active_user)):
    try:
        mg.renew(username,exdate)
        response.status_code = 200
        return {"success":True,"message": "OK","data":""}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}

@router.get("/user-get")
def get_users_(response: Response,
               username:str| None = '',
               current_user: User = Depends(get_current_active_user)):
    if username == 'all':
        try:
            res = mg.select_users()
            response.status_code = 200
            return {"success":True,"message": "OK","data":res}
        except:
            response.status_code = 404
            return {"success":False,"message": "faild","data":""}
    else:
        res = mg.specific_user(username)
        return {"success":True,"message": "OK","data":res}
    
@router.get("/user-kill")
def kill_user_(response: Response,
               username:str,
               server:str,
               current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            obj.killall(username)
            response.status_code = 200
            return {"success":True,"message": "OK","data":""}
        else:
            remote.killall(username,server)
            return {"success":True,"message": "OK","data":""}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}


@router.post("/user-gen")
async def user_gen(response: Response,
                   multi:int,
                   exdate:str,
                   count:int,
                   server:str,
                   current_user: User = Depends(get_current_active_user)):
    try:
        ordered_by=current_user.username
        if server == 'localhost':
            res = await obj.user_passwd_gen(multi,exdate,count,server,ordered_by)
            response.status_code = 200
            return {"success":True,"message": "OK","data":res}
        else:
            res = await remote.user_passwd_gen(multi,exdate,count,server,ordered_by)
            response.status_code = 200
            return {"success":True,"message": "OK","data":res}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}
    
@router.post("/user-del-kill")
async def del_kill_users(response: Response,items: List[str],mode:str,server:str):
    try:
        if server == 'localhost':
            if mode == 'del':
                for user in items:
                    obj.del_user(user)
                response.status_code = 200
                return {"success":True,"message": "OK","data":""}
            elif mode == 'kill':
                for user in items:
                    obj.killall(user)
                response.status_code = 200
                return {"success":True,"message": "OK","data":""}
        else:
            if mode == 'del':
                for user in items:
                    remote.del_user(server,user)
                response.status_code = 200
                return {"success":True,"message": "OK","data":""}
            elif mode == 'kill':
                for user in items:
                    remote.killall(user,server)
                response.status_code = 200
                return {"success":True,"message": "OK","data":""}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}
    
@router.get("/user-search")
def search_user(response: Response,
                username:str,
                current_user: User = Depends(get_current_active_user)):
    try:
        res = mg.select_like(username)
        response.status_code = 200
        return {"success":True,"message": "OK","data":res}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}

@router.get("/user-change-detail")
def change_detail(response: Response,
                    username:str,
                    telegram_id:str | None = '',
                    phone:int | None = '',
                    email:str | None = '',
                    traffic:str | None = '',
                    server:str | None = '',
                    current_user: User = Depends(get_current_active_user)):
    try:
        mg.change_detail_user(username,telegram_id,phone,email,traffic,server)
        response.status_code = 200
        return {"success":True,"message": "OK","data":""}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}
    
@router.get("/user-change-status")
def change_status(response: Response,
                    username:str,
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
            response.status_code = 200
            return {"success":True,"message": "OK","data":{'username':username,'status':status}}
        else:
            dict_remote={
                'unlock':remote.unlockuser,
                'lock':remote.lockuser,
            }
            dict_remote.get(status)(username)(server)
            response.status_code = 200
            return {"success":True,"message": "OK","data":{'username':username,'status':status}}
    except Exception as e :
        print(e)
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}

@router.get("/user-change-multi")
def change_multi(response: Response,
                    username:str,
                    multi:int,
                    current_user: User = Depends(get_current_active_user)):
    try:
        mg.update_multi(username,multi)
        response.status_code = 200
        return {"success":True,"message": "OK","data":{'username':username,'multi':multi}}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}
    
@router.get("/user-status")
def status_clients(response: Response,current_user: User = Depends(get_current_active_user)):
    try:
        list = obj.active_user()
        active = len(list)
        all_users = mg.select_users()
        all_users = len(all_users)
        disable_users = mg.select_disable_user()
        disable_users = len(disable_users)
        enable_users = mg.select_enable_user()
        enable_users = len(enable_users)
        js = {
            'total_users':all_users,
            'total_active_users': active,
            'total_enable_users':enable_users,
            'total_disabled_users':disable_users,
        }
        response.status_code = 200
        return {"success":True,"message": "OK","data":js}
    except Exception as e :
        print(e)
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}

@router.get("/user-active")
def active_user_(response: Response,
                 server:str,
                 current_user: User = Depends(get_current_active_user)):
    if server == 'localhost':
        local = obj.active_user()
        response.status_code = 200
        return local
    else:
        res = remote.all_active_users(server)
        response.status_code = 200
        return {"success":True,"message": "OK","data":res}
