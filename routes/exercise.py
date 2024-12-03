from db.connection import get_connection, release_connection
from fastapi import APIRouter,HTTPException,status

exercise_route = APIRouter(prefix='/exercises')


@exercise_route.get('/')
def get_exercises() -> list:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """ SELECT * FROM exercise"""
        cursor.execute(query)
        result = cursor.fetchall()

        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "No exercises found in database")
        return result
    except Exception as e:
        raise HTTPException(e)
    finally:
        if conn:
            release_connection(conn)


@exercise_route.get('/{exercise_id}')
def get_exercises(exercise_id:int) -> list:
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """ SELECT * FROM exercise WHERE exercise_id = %s"""
        cursor.execute(query,(exercise_id,))
        result = cursor.fetchone()

        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= f"No exercise with id {exercise_id} found in database")
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    finally:
        if conn:
            release_connection(conn)

