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


#------------------------------Exercise Schema--------------------------------

class ExerciseBase(BaseModel):
    name:str
    description:Optional[str]=None
    muscle_group:Optional[str]=None
    category:Optional[str]=None
    difficulty_level:Optional[str]=None
    equipment_needed:Optional[bool]=False
    equipment_details:Optional[str]=None
    calories_burnt_per_minute:Optional[float]=None

class CreateExercise(ExerciseBase):
    pass

class DisplayExercise(BaseModel):
    exercise_id:int
    name:str
    description:Optional[str]=None
    muscle_group:Optional[str]=None
    category:Optional[str]=None
    difficulty_level:Optional[str]=None
    equipment_needed:Optional[bool]=False
    equipment_details:Optional[str]=None
    calories_burnt_per_minute:Optional[float]=None
    created_at:datetime
    updated_at:datetime

    class Config:
        from_attributes = True