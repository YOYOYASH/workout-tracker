from typing import List
from fastapi import APIRouter,HTTPException,status,Depends, Request
from db.database import get_db
from sqlalchemy.orm import Session
import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas
from config import Config

import vertexai
from vertexai.generative_models import GenerativeModel,GenerationConfig
from datetime import datetime
from functools import lru_cache
import json

genai_route = APIRouter(prefix='/genai')
logger = setup_logger("genai_route")


vertexai.init(project=Config.PROJECT_ID,location='us-central1')
model = GenerativeModel('gemini-2.0-flash-001')


@genai_route.post('/generate')
async def generate(request:Request,db:Session= Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        user_data =await request.json()
        user_query = user_data['query']
        if user_query is None or user_query == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Query not found in request")

        intent = get_intent(user_query)
        print("Intent: ",intent)

        if 'workout plan generation' in intent.lower():
            print("Generating workout plan....")
            workout_plan = generate_workout_plan(db,current_user)
            workout_plan_data = json.loads(workout_plan)
            print("Plan: ",workout_plan_data)
            print("Saving workout plan to database....")
            save_workout_plan_db(db,current_user,workout_plan_data)
            return {"intent":intent,"workout_plan":workout_plan_data}
        else:
            return {"intent":intent}
            

    except KeyError as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))    
        





def get_intent(query:str):
    try:
        prompt = f"""You are an expert who can generate user's intent from their query. Your task is to generate the intent for the following query: {query} \n
                     The intent should belong from the following categories: \n
                     1. QnA with assistant \n
                     2. Workout Plan Generation \n
                     Return only the intent and not the full response."""
        response = model.generate_content(
            [prompt]
        )
        return response.text
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    

def generate_workout_plan(db:Session,current_user:dict):
    try:
        profile = current_user.profile
        user_preferences = {
        "age": datetime.now().year - profile.date_of_birth.year,
        "gender": profile.gender,
        "fitness_goal": profile.fitness_goal,
        "fitness_level": profile.fitness_level,
        "available_time": profile.available_time,
        "duration_weeks": 4  # Default
    }
        
        exercise_data = get_exercise_json(db)

        prompt = f"""
                    Generate a {user_preferences['duration_weeks']}-week structured workout plan for a {user_preferences['age']}-year-old {user_preferences['gender']}.
                    - Goal: {user_preferences['fitness_goal']}
                    - Fitness Level: {user_preferences['fitness_level']}
                    - Available Time: {user_preferences['available_time']} minutes per session
                    - Include warm-ups, main workouts, and cooldowns.
                    Database Schema Overview:

                        **Workout Plan**:

                        name: Name of the workout plan.

                        description: Brief description of the workout plan.

                        weeks: Number of weeks the plan will run.

                        user_id: ID of the user for whom the plan is created.

                        **Workout Plan Week**:

                        week_number: The week number in the plan (e.g., Week 1, Week 2).

                        **Workout Plan Day**:

                        day_of_week: The day of the week (e.g., Monday, Wednesday).

                        workout_plan_week_id: ID of the week this day belongs to.

                        **Workout Plan Exercise**:

                        exercise_id: ID of the exercise (this will be mapped later based on the exercise name).

                        sets: Number of sets for the exercise.

                        reps: Number of repetitions per set.

                        order: The order in which the exercise should be performed.

                        workout_plan_day_id: ID of the day this exercise belongs to.

                        **Exercise**:

                        For exercise id details refer to this exercise table data : {exercise_data} \n
                        If the exercise doesn't need reps, set reps to 0.

                        Expected Output:

                        A detailed workout plan that includes:

                        A WorkoutPlan with a name, description, and number of weeks.

                        Multiple WorkoutPlanWeek entries, each with a week_number.

                        For each week, multiple WorkoutPlanDay entries with day_of_week.

                        For each day, multiple WorkoutPlanExercise entries with exercise names, sets, reps, and order.

                        Ensure the exercises are selected based on the user's fitness level, available equipment, and fitness goals.
                    - Format response in JSON like:
                    {{
                        "name": "AI-Generated Strength Plan",
                        "description": "A 4-week program for muscle gain",
                        "weeks": [
                            {{
                                "week_number": 1,
                                "days": [
                                    {{
                                        "day": "Monday",
                                        "exercises": [
                                            {{"exercise_id":1,"exercise_name": "Bench Press", "sets": 4, "reps": 10,"order": 1}},
                                            {{"exercise_id":2,"exercise_name": "Squats", "sets": 3, "reps": 12,"order": 2}}
                                        ]
                                    }}
                                ]
                            }}
                        ]
                    }}
                    """
        response = model.generate_content(
            [prompt],
            generation_config=GenerationConfig(
                temperature = 0.4,
                max_output_tokens = 8192,
                response_mime_type="application/json"
            )
        )

        return response.text
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
        

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


@lru_cache(maxsize=128)
def get_exercise_json(db:Session):
    try:
        exercises = db.query(models.Exercise).all()
        data = [row.__dict__ for row in exercises]

        for row in data:
            row.pop('_sa_instance_state')
        
        return json.dumps(data,cls=DateTimeEncoder)
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))
    

def save_workout_plan_db(db:Session,current_user:dict,workout_plan_data:dict):
    try:
        workout_plan = models.WorkoutPlan(user_id=current_user.id,name=workout_plan_data['name'],description=workout_plan_data['description'],weeks=4)
        db.add(workout_plan)
        db.commit()
        db.refresh(workout_plan)

        for week in workout_plan_data['weeks']:
            workout_plan_week = models.WorkoutPlanWeek(workout_plan_id=workout_plan.id,week_number=week['week_number'])
            db.add(workout_plan_week)
            db.commit()
            db.refresh(workout_plan_week)

            for day in week['days']:
                workout_plan_day = models.WorkoutPlanDay(workout_plan_week_id=workout_plan_week.id,day_of_week=day['day'])
                db.add(workout_plan_day)
                db.commit()
                db.refresh(workout_plan_day)

                for exercise in day['exercises']:
                    workout_plan_exercise = models.WorkoutPlanExercise(exercise_id=exercise['exercise_id'],workout_plan_day_id=workout_plan_day.id,sets=exercise['sets'],reps=exercise['reps'],order=exercise['order'])
                    db.add(workout_plan_exercise)
                    db.commit()
                    db.refresh(workout_plan_exercise)
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=str(e))