from pydantic import  BaseModel, EmailStr


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
        from_attributes =True

class UpdateUser(BaseModel):
    email:EmailStr


class FormData(BaseModel):
    username:str
    password:str
    model_config = {"extra": "forbid"}
