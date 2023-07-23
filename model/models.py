from typing import Literal
from pydantic import Field,BaseModel
from beanie import Document


class User(Document):
    user:str
    multi:int
    exdate:str
    telegram_id:str
    phone:int
    email:str 
    referral:str 
    traffic:str 
    desc:str
    passwd:str
    status:Literal['enable', 'disable']
    server:str
    ordered_by:str
    class Settings:
        name = "user"

class Server(Document):
    host:str
    port:int
    username:str
    passwd:str
    status:str
    class Settings:
        name = "server"

class Response(BaseModel):
    success: bool
    massage: str = ""
    data: dict