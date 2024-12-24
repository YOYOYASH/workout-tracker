import time
import psycopg2
from psycopg2 import pool
from config import Config
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    "dbname": Config.DB_NAME,
    "user": Config.DB_USER,
    "password": Config.DB_PASSWORD,
    "host": Config.DB_HOST,
    "port": Config.DB_PORT,

}

# while True:
#     try:
#         connection_pool = psycopg2.pool.SimpleConnectionPool(
#             1, 20, **DB_CONFIG,cursor_factory = RealDictCursor
#         )
#         print("Connection pool created successfully.")
#         break
#     except Exception as error:
#         print("Error creating connection pool:", error)
#         time.sleep(2)
#         connection_pool = None

# def get_connection():
#     if connection_pool:
#         return connection_pool.getconn()
#     else:
#         raise Exception("Connection pool is not initialized.")

# def release_connection(conn):
#     if connection_pool and conn:
#         connection_pool.putconn(conn)

# def close_all_connections():
#     if connection_pool:
#         connection_pool.closeall()
