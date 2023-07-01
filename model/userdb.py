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
    class Settings:
        name = "user"

