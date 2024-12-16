from fastapi import APIRouter, status, Depends,HTTPException, Form
from typing import List
from sqlalchemy.orm import Session


import models
import schemas
from db.database import get_db
from utils.password import hash_password
from oauth2 import get_current_user


users_route = APIRouter(prefix='/users')


@users_route.get('/',response_model=List[schemas.DisplayUser])
def get_users(db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        print(current_user.id)
        users = db.query(models.User).all()
        if len(users) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No user found in database")
        return users
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@users_route.get('/{user_id}',response_model=schemas.DisplayUser)
def get_user(user_id:int,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id {user_id} not found")
        return user
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@users_route.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayUser)
def create_user(user_data: schemas.CreateUser,db:Session = Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter(models.User.email == user_data.email or models.User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User already exists"
            )
        hashed_password = hash_password(user_data.password)
        user_data.password = hashed_password
        user = models.User(**user_data.model_dump())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@users_route.post('/{user_id}/createprofile',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayUserProfile)
def create_profile(user_id: int, profile_data: schemas.UserProfile, db: Session = Depends(get_db),current_user:dict = Depends(get_current_user) ):
    try:
        if user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User does not have permission to update this profile")
        # Check for existing profile
        existing_profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Profile already exists for this user"
            )
        profile = models.UserProfile(user_id=user_id, **profile_data.model_dump())
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    



    





