from fastapi import Depends, FastAPI, Response, HTTPException, status
from contextlib import asynccontextmanager


from routes import users,exercise,auth
from db.database import engine
import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    models.Base.metadata.create_all(bind=engine)
    yield
    pass

app =FastAPI(lifespan=lifespan)


app.include_router(users.users_route)
app.include_router(exercise.exercise_route)
app.include_router(auth.auth_route)






@app.get('/welcome')
def welcome():
    return {"response":"Welcome to a new project"}


