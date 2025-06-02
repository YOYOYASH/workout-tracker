from datetime import timedelta,datetime,timezone
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from config import Config
from db.database import get_db
import models


SECRET_KEY = Config.SECRET_KEY
TOKEN_EXPIRES_IN = 30
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") 

def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRES_IN)
    to_encode.update({"exp":expire})
    encode_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

def verify_access_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token,key=SECRET_KEY,algorithms=ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except jwt.ExpiredSignatureError:
        # Specific handling for expired tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token has expired"
        )
    except InvalidTokenError as e:
        # More detailed error handling
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db:AsyncSession = Depends(get_db)):
    try:
        credentials_exception = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
                )
        username = verify_access_token(token,credentials_exception)
        # user = db.query(models.User).filter(models.User.username == username).first()
        user = (await db.scalars(select(models.User).where(models.User.username == username))).first()
        return user
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) 
