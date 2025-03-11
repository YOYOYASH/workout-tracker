from fastapi import Depends, FastAPI, Response, HTTPException, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from routes import users,exercise,auth,workout,workout_logs,progress,genai
from utils.logger import setup_logger
from db.database import engine
from config import Config 

import uvicorn

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
app.include_router(workout_logs.workout_log_route)
app.include_router(genai.genai_route)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)




@app.get('/welcome')
def welcome():
    return {"response":"Welcome to a new project"}




if __name__ == "__main__":
    print(Config.HOST)
    print(Config.PORT)
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)