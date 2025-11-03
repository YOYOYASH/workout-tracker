import json
from typing import List
from fastapi import APIRouter,HTTPException,status,Depends
from db.database import get_db
# from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import Request

import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas
from utils.cache import cache

exercise_route = APIRouter(prefix='/exercises')
logger = setup_logger("exercise_route")

@exercise_route.get('/',response_model=List[schemas.DisplayExercise])
async def get_exercises(request:Request,db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        # result = db.query(models.Exercise).all()
        limit = request.query_params.get("top")
        cache_key = f"exercises_top_{limit}" if limit else "exercises_all"
        if cache.exists(cache_key):
            logger.info("Fetching exercises from cache")
            exercises = cache.get(cache_key)
            return json.loads(exercises)
        result = (await db.scalars(select(models.Exercise).limit(limit))).all()
        if len(result) == 0:
            logger.warning(f"No exercise found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No exercies found in database")
        logger.info("Users fetched successfully")

        pydantic_data = [schemas.DisplayExercise.model_validate(exercise) for exercise in result]
        # Set the cache
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


@exercise_route.get('/{exercise_id}',response_model=schemas.DisplayExercise)
async def get_exercise(exercise_id:int,db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)) -> list:
    conn = None
    try:
        # query = db.query(models.Exercise).filter(models.Exercise.exercise_id == exercise_id)
        cache_key = f"exercise_{exercise_id}"
        if cache.exists(cache_key):
            logger.info("Fetching exercises for day from cache")
            exercises = cache.get(cache_key)
            return json.loads(exercises)
        query = (await db.scalars(select(models.Exercise).where(models.Exercise.exercise_id == exercise_id)))
        result = query.first()
        if result is None:
            logger.warning(f"No exercise with id {exercise_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No exercise with id {exercise_id} found in database")
        logger.info("Exercise fetched successfully")

        # Set the cache
        pydantic_data = schemas.DisplayExercise.model_validate(result)
        cache.set(
            cache_key,
            json.dumps(pydantic_data.model_dump(mode='json')),
            ex=3600  # Cache for 1 hour
        )

        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

