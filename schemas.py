from pydantic import  BaseModel, EmailStr
from datetime import date,datetime
from typing import Optional

class UserBase(BaseModel):
    username:str
    email: EmailStr
    password:str

class CreateUser(UserBase):
    pass

class DisplayUser(BaseModel):
    id:int
    username: str
    email:str

    class Config:
        from_attributes = True

class UpdateUser(BaseModel):
    email:EmailStr


class UserProfile(BaseModel):
    first_name:str
    last_name:Optional[str]=None
    date_of_birth:date
    height:int
    weight:int
    fitness_goal:Optional[str]=None
    fitness_level:Optional[str]='beginner'
    available_time:Optional[int] = None
    contact_number:int
    created_at:datetime
    updated_at:datetime

class DisplayUserProfile(UserProfile):
    id:int
    user_id:int
    class Config:
        from_attributes = True


class TokenData(BaseModel):
    token:str
    type:str

