from alembic import command
from fastapi import Depends, FastAPI, Response, HTTPException, status
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

import models
from routes import users,exercise,auth,workout,workout_logs,progress,genai
from utils.logger import setup_logger
from db.database import sessionmanger
from config import Config 

import uvicorn

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Run Alembic migrations on startup."""
#     print("Running Alembic migrations...")

#     alembic_cfg = Config("alembic.ini")
#     command.upgrade(alembic_cfg, "head")

#     yield  # Continue running FastAPI after migrations

app =FastAPI()

logger = setup_logger(__name__)

app.include_router(users.users_route,prefix='/api')
app.include_router(exercise.exercise_route,prefix='/api')
app.include_router(auth.auth_route,prefix='/api')
app.include_router(workout.workout_route,prefix='/api')
app.include_router(workout_logs.workout_log_route,prefix='/api')
app.include_router(genai.genai_route,prefix='/api')
app.include_router(progress.progress_route,prefix='/api')


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)




@app.get("/api/")
async def root():
    return {"message": "Hello World"}




if __name__ == "__main__":
    print(Config.HOST)
    print(Config.PORT)
    uvicorn.run(app, host=Config.HOST, port=Config.PORT)