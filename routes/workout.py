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
        exercise_already_exists = db.query(models.WorkoutPlanExercise).filter(models.WorkoutPlanExercise.workout_plan_id == workout_id,models.WorkoutPlanExercise.exercise_id == exercise_data.exercise_id).first()
        if exercise_already_exists:
            logger.warning(f"Exercise already exists in workout plan")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail= f"Exercise already exists in workout plan")
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
    

@workout_route.get('/{workout_id}/exercises',response_model=List[schemas.DisplayWorkoutPlanExercise])
def get_workout_exercises(workout_id:int,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)) -> list:
    try:
        query = db.query(models.WorkoutPlanExercise).filter(models.WorkoutPlanExercise.workout_plan_id == workout_id)
        result = query.all()
        if len(result) == 0:
            logger.warning(f"No exercise found for workout plan with id {workout_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No exercise found for workout plan with id {workout_id}")
        logger.info("Exercises fetched successfully")
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.put('/{workout_id}/exercises',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayWorkoutPlanExercise)
def update_workout_exercises(workout_id:int,exercise_data: List[schemas.UpdateExerciseInWorkout] ,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        workout_exercise_exists = db.query(models.WorkoutPlanExercise).join(models.WorkoutPlan).filter(
                                models.WorkoutPlanExercise.workout_plan_id == workout_id,
                                models.WorkoutPlan.user_id == current_user.id
                            ).first()

        if workout_exercise_exists is None:
            logger.warning(f"No workout plan with id {workout_id} found in database or user does not have access to it")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout plan with id {workout_id} found in database or user does not have access to it")

        workout_exercises = []
        for exercise in exercise_data:
            workout_exercise = db.query(models.WorkoutPlanExercise).filter(models.WorkoutPlanExercise.workout_plan_id == workout_id,
                                                                           models.WorkoutPlanExercise.exercise_id == exercise.exercise_id).first()
            if workout_exercise is None:
                logger.warning(f"No exercise with id {exercise.exercise_id} found in database")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No exercise with id {exercise.exercise_id} found in database")
            for key,value in exercise.model_dump().items():
                setattr(workout_exercise,key,value)
            db.add(workout_exercise)
            workout_exercises.append(workout_exercise)
        db.commit()
        for exercise in workout_exercises:
            db.refresh(exercise)
        logger.info("Exercises updated successfully")
        return workout_exercise
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.delete('/{workout_id}/exercises/{exercise_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_workout_exercise(workout_id:int,exercise_id:int,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        workout_exercise = db.query(models.WorkoutPlanExercise).join(models.WorkoutPlan).filter(
                                models.WorkoutPlanExercise.workout_plan_id == workout_id,
                                models.WorkoutPlanExercise.exercise_id == exercise_id,
                                models.WorkoutPlan.user_id == current_user.id
                            ).first()
        if workout_exercise is None:
            logger.warning(f"No workout plan with id {workout_id} found in database or user does not have access to it")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout plan with id {workout_id} found in database or user does not have access to it")
        db.delete(workout_exercise)
        db.commit()
        logger.info("Exercise deleted successfully")
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.delete('/{workout_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_workout(workout_id:int,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        workout_plan_owner = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.user_id == current_user.id).first()
        if workout_plan_owner is None:
            logger.warning(f"user does not have access to delete this workout")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"User does not have access to delete this workout")
        workout = db.query(models.WorkoutPlan).filter(models.WorkoutPlan.id == workout_id).first()
        if workout is None:
            logger.warning(f"No workout plan with id {workout_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No workout plan with id {workout_id} found in database")
        db.delete(workout)
        db.commit()
        logger.info("Workout plan deleted successfully")
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))