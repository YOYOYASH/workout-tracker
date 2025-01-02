from typing import List
from fastapi import APIRouter,HTTPException,status,Depends
from db.database import get_db
from sqlalchemy.orm import Session
import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas

exercise_route = APIRouter(prefix='/exercises')
logger = setup_logger("exercise_route")

@exercise_route.get('/',response_model=List[schemas.DisplayExercise])
def get_exercises(db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)) -> list:
    conn = None
    try:
        result = db.query(models.Exercise).all()
        if len(result) == 0:
            logger.warning(f"No exercise found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No exercies found in database")
        logger.info("Users fetched successfully")
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@exercise_route.get('/{exercise_id}',response_model=schemas.DisplayExercise)
def get_exercises(exercise_id:int,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)) -> list:
    conn = None
    try:
        query = db.query(models.Exercise).filter(models.Exercise.exercise_id == exercise_id)
        result = query.first()
        if result is None:
            logger.warning(f"No exercise with id {exercise_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No exercise with id {exercise_id} found in database")
        logger.info("Exercise fetched successfully")
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

