from fastapi import FastAPI, Response, HTTPException, status
from pydantic import  BaseModel, EmailStr
from routes import users,exercise
app =FastAPI()


app.include_router(users.users_route)
app.include_router(exercise.exercise_route)


class User(BaseModel):
    user_id:int
    name:str
    email:EmailStr
    age:int
    location:str
    is_active:bool

@app.get('/welcome')
def welcome():
    return {"response":"Welcome to a new project"}


