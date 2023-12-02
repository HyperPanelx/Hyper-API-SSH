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

remote = MultiOps()
mg = dbinsert()
obj=sshtnl()
router = APIRouter(tags=['Server'])

@router.get("/server-add", dependencies=[Depends(has_permission)])
async def add_server(ip_address:str,
                port:int,
                user:str,
                password:str,
                response: Response,
                current_user: User = Depends(get_current_active_user)):
    try:
        await mg.add_server(ip_address,port,user,password)
        response.status_code = 200
        return {"success":True,"message": "OK","data":""}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}
    
@router.get("/server-change-status", dependencies=[Depends(has_permission)])
async def add_server(ip_address:str,
                status:str,
                response: Response,
                current_user: User = Depends(get_current_active_user)):
    try:
        mg.update_status_server(ip_address,status)
        response.status_code = 200
        return {"success":True,"message": "OK","data":""}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}


@router.get("/server-list")
async def list_servers(response: Response,current_user: User = Depends(get_current_active_user)):
    try:
        res = remote.check_status_server()
        response.status_code = 200
        return {"success":True,"message": "OK","data":res}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}

@router.get("/server-resource-usage")
def resource_usage(response: Response,server:str,current_user: User = Depends(get_current_active_user)):
    try:
        if server == 'localhost':
            res = obj.res_usage()
            net = obj.network_usage()
            response.status_code = 200
            return res,net
        else:
            res = remote.res_usage(server)
            return {"success":True,"message": "OK","data":res}
    except Exception as e :
        print(e)
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}