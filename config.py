from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")  # Default to 'localhost' if not provided
    DB_PORT = int(os.getenv("DB_PORT", 5432))   # Default to 5432 if not provided
    APP_ENV = os.getenv("APP_ENV", "local")
    SECRET_KEY= os.getenv("SECRET_KEY")
    PROJECT_ID = os.getenv("PROJECT_ID")
    HOST = os.getenv("HOST")
    PORT = os.getenv("PORT")