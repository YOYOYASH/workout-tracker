import json
from typing import List
from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy import select
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas
from utils.cache import cache

workout_log_route = APIRouter(prefix='/workout_logs')
logger = setup_logger("workout_logs_route")

@workout_log_route.post('/',status_code=status.HTTP_201_CREATED)
async def create_workout_log(workout_log_data: schemas.CreateWorkoutLog,db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        workout_plan = (await db.scalars(select(models.WorkoutPlan).where(models.WorkoutPlan.id == workout_log_data.workout_plan_id))).first()
        if workout_plan is None:
            logger.warning(f"No workout plan with id {workout_log_data.workout_plan_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout plan with id {workout_log_data.workout_plan_id} found in database")
        
        new_workout_log = models.WorkoutLog(user_id=current_user.id,**workout_log_data.model_dump())
        db.add(new_workout_log)
        await db.commit()
        await db.refresh(new_workout_log)
        logger.info("Workout log created successfully")
        cache_key = f"workout_logs_user_{current_user.id}"
        if cache.exists(cache_key):
            logger.info("Invalidating cache for workout logs")
            cache.delete(cache_key)
        return new_workout_log
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_log_route.post('/{workout_log_id}/exercises',response_model=List[schemas.DisplayWorkoutLogExercise],status_code=status.HTTP_201_CREATED)
async def add_exercise_to_workout_log(workout_log_id:int,exercise_data: List[schemas.AddExerciseToWorkoutLog],db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        workout_log = (await db.scalars(select(models.WorkoutLog).where(models.WorkoutLog.id == workout_log_id))).first()
        if workout_log is None:
            logger.warning(f"No workout log with id {workout_log_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout log with id {workout_log_id} found in database")
        # new_workout_log_exercise = models.WorkoutLogExercise(workout_log_id=workout_log_id,**exercise_data.model_dump())
        new_workout_log_exercises = []
        for exercise in exercise_data:
            new_workout_log_exercise = models.WorkoutLogExercise(
                workout_log_id=workout_log_id,
                **exercise.model_dump(exclude_unset=True)  # Exclude unset fields
            )
            new_workout_log_exercises.append(new_workout_log_exercise)
        db.add_all(new_workout_log_exercises)
        await db.commit()
        result = (await db.scalars(
            select(models.WorkoutLogExercise).where(
                models.WorkoutLogExercise.workout_log_id == workout_log_id
            )
        )).all()
        logger.info("Workout log exercise created successfully")
        cache_key = f"workout_log_exercises_{workout_log_id}"
        if cache.exists(cache_key):
            logger.info("Invalidating cache for workout log exercises")
            cache.delete(cache_key)
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_log_route.get('/',response_model=List[schemas.DisplayWorkoutLog])
async def get_workout_logs(db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        cache_key = f"workout_logs_user_{current_user.id}"
        if cache.exists(cache_key):
            logger.info("Fetching workout logs from cache")
            workout_logs = cache.get(cache_key)
            return json.loads(workout_logs)
        result = (await db.scalars(select(models.WorkoutLog).where(models.WorkoutLog.user_id == current_user.id))).all()
        if len(result) == 0:
            logger.warning(f"No workout log found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No workout log found in database")
        logger.info("Workout logs fetched successfully")
        # Set the cache
        pydantic_data = [schemas.DisplayWorkoutLog.model_validate(workout_log) for workout_log in result]

        cache.set(
            cache_key,
            json.dumps([data.model_dump(mode='json') for data in pydantic_data]),
            ex=3600  # Cache for 1 hour
        )
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@workout_log_route.get('/{workout_log_id}/exercises')
async def get_workoutlog_exercises(workout_log_id:int,db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        # result = db.query(models.WorkoutLogExercise).filter(models.WorkoutLogExercise.workout_log_id == workout_log_id).all()
        cache_key = f"workout_log_exercises_{workout_log_id}"
        if cache.exists(cache_key):
            logger.info("Fetching workout log exercises from cache")
            exercises = cache.get(cache_key)
            return json.loads(exercises)
        result = (await db.scalars(select(models.WorkoutLogExercise).where(models.WorkoutLogExercise.workout_log_id == workout_log_id))).all()
        if len(result) == 0:
            logger.warning("No exercises logged for this workout")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No exercises logged for this workout")
        logger.info("Exercise logs fetched successfully!!!")
        # Set the cache
        pydantic_data = [schemas.DisplayWorkoutLogExercise.model_validate(exercise) for exercise in result]
        cache.set(
            cache_key,
            json.dumps([data.model_dump(mode='json') for data in pydantic_data]),
            ex=3600  # Cache for 1 hour
        )
        return pydantic_data
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
