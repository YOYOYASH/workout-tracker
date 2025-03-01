from typing import List
from fastapi import APIRouter,HTTPException,status,Depends
from db.database import get_db
from sqlalchemy.orm import Session
import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas


progress_route = APIRouter(prefix='/progress')


logger = setup_logger("progress_route")


@progress_route.post('/',status_code=status.HTTP_201_CREATED, response_model=schemas.DisplayProgress)
def create_progress(progress_data: schemas.CreateProgress,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        new_progress = models.Progress(user_id=current_user.id,**progress_data.model_dump())
        db.add(new_progress)
        db.commit()
        db.refresh(new_progress)
        logger.info("Progress created successfully")
        return new_progress
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@progress_route.get('/',response_model=List[schemas.DisplayProgress])
def get_progress(db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        result = db.query(models.Progress).filter(models.Progress.user_id == current_user.id).all()
        if len(result) == 0:
            logger.warning(f"No progress found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No progress found in database")
        logger.info("Progress fetched successfully")
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@progress_route.get('/{progress_id}',response_model=schemas.DisplayProgress)
def get_progress_by_id(progress_id:int,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        progress = db.query(models.Progress).filter(models.Progress.id == progress_id).first()
        if progress is None:
            logger.warning(f"No progress with id {progress_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Progress with id {progress_id} not found")
        logger.info("Progress fetched successfully")
        return progress
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    

@progress_route.put('/{progress_id}',response_model=schemas.DisplayProgress)
def update_progress(progress_id:int,progress_data:schemas.CreateProgress,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        progress = db.query(models.Progress).filter(models.Progress.id == progress_id).first()
        if progress is None:
            logger.warning(f"No progress with id {progress_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Progress with id {progress_id} not found")
        for key,value in progress_data.model_dump().items():
            setattr(progress,key,value)
        db.commit()
        db.refresh(progress)
        logger.info("Progress updated successfully")
        return progress
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@progress_route.delete('/{progress_id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_progress(progress_id:int,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        progress = db.query(models.Progress).filter(models.Progress.id == progress_id).first()
        if progress is None:
            logger.warning(f"No progress with id {progress_id} found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Progress with id {progress_id} not found")
        db.delete(progress)
        db.commit()
        logger.info("Progress deleted successfully")
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))