from fastapi import Depends, FastAPI, Response, HTTPException, status
from contextlib import asynccontextmanager


from routes import users,exercise,auth,workout
from utils.logger import setup_logger
from db.database import engine
import models


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     models.Base.metadata.create_all(bind=engine)
#     yield
#     pass

app =FastAPI()

logger = setup_logger(__name__)

app.include_router(users.users_route)
app.include_router(exercise.exercise_route)
app.include_router(auth.auth_route)
app.include_router(workout.workout_route)






@app.get('/welcome')
def welcome():
    return {"response":"Welcome to a new project"}


