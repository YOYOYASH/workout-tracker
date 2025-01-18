from typing import List
from fastapi import APIRouter,HTTPException,status,Depends
from db.database import get_db
from sqlalchemy.orm import Session
import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas

workout_route = APIRouter(prefix='/workouts')
logger = setup_logger("workout_route")

@workout_route.get('/',response_model=List[schemas.DisplayWorkoutPlan])
def get_workouts(db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)) -> list:
    try:
        result = db.query(models.WorkoutPlan).all()
        if len(result) == 0:
            logger.warning(f"No workout plan found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No workout plan found in database")
        logger.info("Workout plans fetched successfully")
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.get('/{workout_id}',response_model=schemas.DisplayWorkoutPlan)
def get_workout(workout_id:int,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)) -> list:
    try:
        query = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.id == workout_id)
        result = query.first()
        if result is None:
            logger.warning(f"No workout plan with id {workout_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout plan with id {workout_id} found in database")
        logger.info("Workout plan fetched successfully")
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayWorkoutPlan)
def create_workout(workout_data: schemas.CreateWorkoutPlan,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        new_workout = models.WorkoutPlan(user_id=current_user.id,**workout_data.model_dump())
        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)
        logger.info("Workout plan created successfully")
        return new_workout
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@workout_route.post('/{workout_id}/exercises',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayWorkoutPlanExercise)
def add_exercise_to_workout(workout_id:int,exercise_data: schemas.AddExerciseToWorkout,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        workout = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.id == workout_id).first()
        if workout is None:
            logger.warning(f"No workout plan with id {workout_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout plan with id {workout_id} found in database")
        exercises = db.query(models.Exercise).filter(models.Exercise.exercise_id == exercise_data.exercise_id).first()
        if exercises is None:
            logger.warning(f"No exercise with id {exercise_data.exercise_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No exercise with id {exercise_data.exercise_id} found in database")
        new_exercise = models.WorkoutPlanExercise(workout_plan_id=workout_id,**exercise_data.model_dump())
        db.add(new_exercise)
        db.commit()
        db.refresh(new_exercise)
        logger.info("Exercise added to workout plan successfully")
        return new_exercise
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
