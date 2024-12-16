from fastapi import APIRouter,status,Depends,HTTPException,Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Annotated

from db.database import get_db
import schemas
import models
from utils.password import verify_password
from oauth2 import create_access_token


auth_route = APIRouter()


@auth_route.post('/login')
def login_user(user_credentials: Annotated[OAuth2PasswordRequestForm, Depends()],db:Session = Depends(get_db)):
    try:
        user = db.query(models.User).filter(models.User.username == user_credentials.username).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid credentials")
        if not verify_password(user.password,user_credentials.password):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Invalid credentials")
        access_token = create_access_token({"sub":user.username})
        return schemas.TokenData(token=access_token,type='bearer')
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        