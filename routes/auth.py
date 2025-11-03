from fastapi import APIRouter,status,Depends,HTTPException,Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Annotated
from supabase import create_client, Client

from db.database import get_db
import schemas
import models
from utils.password import verify_password
from oauth2 import create_access_token, get_current_user
from config import Config
import os


auth_route = APIRouter()

# Initialize Supabase client
SUPABASE_URL = Config.SUPABASE_URL
SUPABASE_KEY = Config.SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@auth_route.post('/login')
async def login_user(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()]):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_credentials.username,
            "password": user_credentials.password,
        })
        
        if response.user is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")

        # Verify the user using get_current_user (assuming it's adapted for Supabase)
        # This step might need adjustment based on how get_current_user is implemented
        # For now, we'll assume get_current_user can handle the Supabase session
        # and we'll pass the access token to it.
        # Note: get_current_user typically expects a token from the Authorization header.
        # We'll need to simulate that or adapt get_current_user.
        # For this example, we'll just return the token from sign_in_with_password.
        # The actual verification with get_current_user would happen in protected routes.
        
        access_token = response.session.access_token
        return schemas.TokenData(token=access_token, type='bearer')
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        