from fastapi import (FastAPI,
                     Depends,
                     status,
                     Body,
                     Response,
                     HTTPException)
from datetime import  timedelta
from typing import List
from db.mongo import dbinsert
from fastapi.security import OAuth2PasswordRequestForm
from security.main import *
from fastapi.middleware.cors import CORSMiddleware
from routes.routes_users import router as routes_user
from routes.routes_server import router as routes_server
from fastapi.responses import JSONResponse
app = FastAPI()
mg = dbinsert()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.exception_handler(HTTPException)
async def handle_http_exception(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success":False,"message": "Not authenticated","data":''}
    )
@app.on_event("startup")
async def start_db():
    await mg.init_db()

@app.post("/token", response_model=Token,tags=['Login'])
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

@app.get("/panel/me/", response_model=User,tags=['Login'])
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/panel/create/",tags=['Login'])
def user_create(response: Response,
                username:str,
                passwd:str,
                role:int,
                current_user: User = Depends(get_current_active_user)):
    try:
        hashpass = hash_pass(passwd)
        add_user(username,hashpass,role)
        response.status_code = 200
        return {"success":True,"message": "OK","data":""}
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}
    
@app.get("/panel/delete/",tags=['Login'])
def user_create(response: Response,
                username:str,
                current_user: User = Depends(get_current_active_user)):
    try:
        
        mg.del_user_panel(username)
        response.status_code = 200
        return {"success":True,"message": "OK","data":""} 
    except:
        response.status_code = 404
        return {"success":False,"message": "faild","data":""}
app.include_router(routes_server)
app.include_router(routes_user)

@app.get("/notify",tags=['Notif'])
def notify():
    return [
   { 
        "title":"test",
        "content":"test",
        "link":"test"
    }
    ]
