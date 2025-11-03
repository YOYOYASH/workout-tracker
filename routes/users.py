import json
from fastapi import APIRouter, status, Depends,HTTPException, Form
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from utils.cache import cache
from utils.logger import setup_logger


import models
import schemas
from db.database import get_db
from utils.password import hash_password
from oauth2 import get_current_user


users_route = APIRouter(prefix='/users')
logger = setup_logger("users_route")

@users_route.get('/',response_model=List[schemas.DisplayUser])
async def get_users(db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        users = (await db.scalars(select(models.User))).all()
        if len(users) == 0:
            logger.warning(f"No user found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No user found in database")
        logger.info("Users fetched successfully")
        return users
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@users_route.get('/{user_id}')
async def get_user(user_id:str,db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        # user = db.query(models.User).options(joinedload(models.User.profile)).filter(models.User.id == user_id).first()
        if user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User does not have permission to update this profile")
        cache_key = f"user_{user_id}"
        if cache.exists(cache_key):
            logger.info("Fetching user from cache")
            user = cache.get(cache_key)
            return json.loads(user)
        user_profile = (await db.scalars(select(models.UserProfile).where(models.UserProfile.user_id == user_id)
                              )).first() 
        if user_profile is None:
            logger.warning(f"No profile found for user with id {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No profile found for user with id {user_id}")
        logger.info("User profile fetched successfully")

        pydantic_data = schemas.DisplayUserProfile.model_validate(user_profile)

        cache.set(
            cache_key,
            json.dumps(pydantic_data.model_dump(mode='json'))
        )

        return user_profile
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        print(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@users_route.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayUser)
async def create_user(user_data: schemas.CreateUser,db:AsyncSession = Depends(get_db)):
    try:
        existing_user = (await db.scalars(select(models.User).where(models.User.email == user_data.email or models.User.username == user_data.username))).first()
        if existing_user:
            logger.warning(f"User already exisits")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="User already exists"
            )
        hashed_password = hash_password(user_data.password)
        user_data.password = hashed_password
        user = models.User(**user_data.model_dump())
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"User with id {user.id} added successfully")
        return user
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@users_route.post('/{user_id}/createprofile',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayUserProfile)
async def create_profile(user_id: str, profile_data: schemas.UserProfile, db: AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user) ):
    try:
        print(f"Current user ID: {current_user.id}")
        if user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User does not have permission to update this profile")
        # Check for existing profile
        existing_profile = (await db.scalars(select(models.UserProfile).where(models.UserProfile.user_id == user_id))).first()
        if existing_profile:
            logger.warning(f"User profile for id  {user_id} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Profile already exists for this user"
            )
        profile = models.UserProfile(user_id=user_id, **profile_data.model_dump())
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        logger.info("User profile created successfully")
        return profile
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@users_route.put('/{user_id}/updateprofile',response_model=schemas.DisplayUserProfile)
async def update_profile(user_id:str,profile_data:schemas.UpdateUserProfile,db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        if user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="User does not have permission to update this profile")
        profile = (await db.scalars(select(models.UserProfile).where(models.UserProfile.user_id == user_id))).first()
        if profile is None:
            logger.warning(f"No profile found for user with id {user_id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No profile found for user with id {user_id}")
        for key,value in profile_data.model_dump().items():
            setattr(profile,key,value)
        await db.commit()
        await db.refresh(profile)
        logger.info("User profile updated successfully")
        cache_key = f"user_{user_id}"
        if cache.exists(cache_key):
            cache.delete(cache_key)
        return profile
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))





    





