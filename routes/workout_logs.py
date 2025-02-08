from typing import List
from fastapi import APIRouter,HTTPException,status,Depends
from db.database import get_db
from sqlalchemy.orm import Session
import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas

workout_log_route = APIRouter(prefix='/workout_logs')
logger = setup_logger("workout_logs_route")

@workout_log_route.post('/',status_code=status.HTTP_201_CREATED)
def create_workout_log(workout_log_data: schemas.CreateWorkoutLog,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        workout_plan = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.id == workout_log_data.workout_plan_id).first()
        if workout_plan is None:
            logger.warning(f"No workout plan with id {workout_log_data.workout_plan_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout plan with id {workout_log_data.workout_plan_id} found in database")
        
        new_workout_log = models.WorkoutLog(user_id=current_user.id,**workout_log_data.model_dump())
        db.add(new_workout_log)
        db.commit()
        db.refresh(new_workout_log)
        logger.info("Workout log created successfully")
        return new_workout_log
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_log_route.post('/{workout_log_id}/exercises',response_model=schemas.DisplayWorkoutLogExercise,status_code=status.HTTP_201_CREATED)
def add_exercise_to_workout_log(workout_log_id:int,exercise_data: schemas.AddExerciseToWorkoutLog,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        workout_log = db.query(models.WorkoutLog).filter(models.WorkoutLog.id == workout_log_id).first()
        if workout_log is None:
            logger.warning(f"No workout log with id {workout_log_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout log with id {workout_log_id} found in database")
        new_workout_log_exercise = models.WorkoutLogExercise(workout_log_id=workout_log_id,**exercise_data.model_dump())
        db.add(new_workout_log_exercise)
        db.commit()
        db.refresh(new_workout_log_exercise)
        logger.info("Workout log exercise created successfully")
        return new_workout_log_exercise
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_log_route.get('/',response_model=List[schemas.DisplayWorkoutLog])
def get_workout_logs(db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)) -> list:
    try:
        result = db.query(models.WorkoutLog).filter(models.WorkoutLog.user_id == current_user.id).all()
        if len(result) == 0:
            logger.warning(f"No workout log found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No workout log found in database")
        logger.info("Workout logs fetched successfully")
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))