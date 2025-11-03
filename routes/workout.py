import json
from typing import List
from fastapi import APIRouter,HTTPException,status,Depends
from db.database import get_db
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas
from utils.cache import cache

workout_route = APIRouter(prefix='/workouts')
logger = setup_logger("workout_route")

@workout_route.get('/',response_model=List[schemas.DisplayWorkoutPlan])
async def get_workouts(db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        # result = db.query(models.WorkoutPlan).all()
        cache_key  = f"user:{current_user.id}:workouts"
        if cache.exists(cache_key):
            logger.info("Fetching workout plans from cache")
            result = cache.get(f"user:{current_user.id}:workouts")
            print(type(result))
            return json.loads(result)
        result  = (await db.scalars(select(models.WorkoutPlan).where(models.WorkoutPlan.user_id == current_user.id))).all()
        if len(result) == 0:
            logger.warning(f"No workout plan found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No workout plan found in database")
        logger.info("Workout plans fetched successfully")
        # Convert to Pydantic models
        pydantic_data = [schemas.DisplayWorkoutPlan.model_validate(item) for item in result]

        # Cache the result
        cache.set(
            cache_key,
            json.dumps([item.model_dump(mode='json') for item in pydantic_data]),
            ex=3600
        )  # Cache for 1 hour
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.get("/{plan_id}")
async def get_workout_plan(
    plan_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    # plan = db.query(models.WorkoutPlan).filter(
    #     models.WorkoutPlan.id == plan_id, models.WorkoutPlan.user_id == current_user.id
    # ).first()
    cache_key = f"user:{current_user.id}:workout_plan:{plan_id}"
    if cache.exists(cache_key):
        logger.info("Fetching workout plan from cache")
        plan = cache.get(cache_key)
        return json.loads(plan)
    plan = (await db.scalars(select(models.WorkoutPlan).where(models.WorkoutPlan.id == plan_id,models.WorkoutPlan.user_id == current_user.id)
                            .options(
                                # Eagerly load 'weeks_schedule' relationship
                                selectinload(models.WorkoutPlan.weeks_schedule)
                                # And within each week, eagerly load its 'days_schedule'
                                .selectinload(models.WorkoutPlanWeek.days_schedule)
                            )
                             )).fetchall()
            
    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found.")
    
    # Because of `selectinload` and `response_model=WorkoutPlanResponse` with `from_attributes=True`,
    # FastAPI (with Pydantic) can often automatically convert the `plan` ORM object
    # (with its eagerly loaded relationships) into the Pydantic response model.

    # The `plan` object now has:
    # - plan.id, plan.name, plan.description, plan.weeks (the integer)
    # - plan.weeks_schedule (a list of WorkoutPlanWeek objects)
    #   - Each week_obj in plan.weeks_schedule has week_obj.days_schedule (a list of WorkoutPlanDay objects)
    
    pydantic_plan = [schemas.DisplayWorkoutPlanResponse.model_validate(item) for item in plan]
    #Set the cache
    cache.set(
        cache_key,
        json.dumps([item.model_dump(mode='json') for item in pydantic_plan]),
        ex=3600  # Cache for 1 hour
    )

    return plan # FastAPI will use WorkoutPlanResponse to serialize this

@workout_route.get("/days/{day_id}/exercises", response_model=List[schemas.DisplayWorkoutPlanExercise])
async def get_exercises_in_day(
    day_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    # day = db.query(models.WorkoutPlanDay).join(models.WorkoutPlanWeek).join(models.WorkoutPlan).filter(
    #     models.WorkoutPlanDay.id == day_id, 
    #     models.WorkoutPlan.user_id == current_user.id
    # ).first()
    cache_key = f"user:{current_user.id}:workout_day_exercises:{day_id}"
    if cache.exists(cache_key):
        logger.info("Fetching exercises for day from cache")
        exercises = cache.get(cache_key)
        return json.loads(exercises)
    day = (await db.scalars(select(models.WorkoutPlanDay).join(models.WorkoutPlanWeek).join(models.WorkoutPlan).where(
        models.WorkoutPlanDay.id == day_id,
        models.WorkoutPlan.user_id == current_user.id
    ))).first()

    if not day:
        raise HTTPException(status_code=404, detail="Day not found or unauthorized access.")
    


    # exercises = db.query(models.WorkoutPlanExercise).filter(models.WorkoutPlanExercise.workout_plan_day_id == day_id).all()
    exercises = (await db.scalars(select(models.WorkoutPlanExercise).where(models.WorkoutPlanExercise.workout_plan_day_id == day_id))).all()

    #cache the result
    pydantic_exercises = [schemas.DisplayWorkoutPlanExercise.model_validate(item) for item in exercises]
    cache.set(
        cache_key,
        json.dumps([item.model_dump(mode='json') for item in pydantic_exercises]),
        ex=3600  # Cache for 1 hour
    )

    return exercises


@workout_route.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayWorkoutPlan)
async def create_workout(workout_data: schemas.CreateWorkoutPlan,db:AsyncSession = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        cache_key = f"user:{current_user.id}:workouts"
        if cache.exists(cache_key):
            logger.info("clearing cache for workout plans")
            cache.delete(cache_key)

        new_workout = models.WorkoutPlan(user_id=current_user.id,**workout_data.model_dump())
        db.add(new_workout)
        await db.commit()
        await db.refresh(new_workout)
        logger.info("Workout plan created successfully")
        return new_workout
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.post("/{plan_id}/weeks", response_model=schemas.DisplayWeek)
async def add_week_to_plan(
    plan_id: int, 
    week_data: schemas.CreateWeek, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    # workout_plan = db.query(models.WorkoutPlan).filter(
    #     models.WorkoutPlan.id == plan_id, models.WorkoutPlan.user_id == current_user.id
    # ).first()
    workout_plan = (await db.scalars(select(models.WorkoutPlan).where(models.WorkoutPlan.id == plan_id,models.WorkoutPlan.user_id == current_user.id))).first()

    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found or unauthorized access.")
    
    if week_data.week_number < 1 or week_data.week_number > workout_plan.weeks:
        raise HTTPException(status_code=400, detail=f"Invalid week number. Must be between 1 and {workout_plan.weeks}.")

    # Prevent duplicate weeks
    existing_week = (await db.scalars(select(models.WorkoutPlanWeek).where(
        models.WorkoutPlanWeek.workout_plan_id == plan_id,
        models.WorkoutPlanWeek.week_number == week_data.week_number
    ))).first()

    if existing_week:
        raise HTTPException(status_code=400, detail=f"Week {week_data.week_number} already exists in this plan.")

    try:
        week = models.WorkoutPlanWeek(
            workout_plan_id=plan_id,
            week_number=week_data.week_number
        )
        db.add(week)
        await db.commit()
        await db.refresh(week)
        return week

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding week: {str(e)}")


@workout_route.post("/weeks/{week_id}/days", response_model=schemas.DisplayWorkoutDay)
async def add_day_to_week(
    week_id: int, 
    day_data: schemas.CreateWorkoutDay, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    # week = db.query(models.WorkoutPlanWeek).join(models.WorkoutPlan).filter(
    #     models.WorkoutPlanWeek.id == week_id, 
    #     models.WorkoutPlan.user_id == current_user.id
    # ).first()
    week = (await db.scalars(select(models.WorkoutPlanWeek).join(models.WorkoutPlan).where(
        models.WorkoutPlanWeek.id == week_id, 
        models.WorkoutPlan.user_id == current_user.id
    )))

    if not week:
        raise HTTPException(status_code=404, detail="Week not found or unauthorized access.")

    # Prevent duplicate days
    existing_day = (await db.scalars(select(models.WorkoutPlanDay).where(
        models.WorkoutPlanDay.workout_plan_week_id == week_id,
        models.WorkoutPlanDay.day_of_week == day_data.day_of_week
    ))).first()

    if existing_day:
        raise HTTPException(status_code=400, detail=f"{day_data.day_of_week} already exists in this week.")

    try:
        day = models.WorkoutPlanDay(
            workout_plan_week_id=week_id,
            day_of_week=day_data.day_of_week
        )
        db.add(day)
        await db.commit()
        await db.refresh(day)
        return day

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding day: {str(e)}")


@workout_route.post("/days/{day_id}/exercises", response_model=schemas.DisplayWorkoutPlanExercise)
async def add_exercise_to_day(
    day_id: int, 
    exercise_data: schemas.AddExerciseToWorkout, 
    db: AsyncSession = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    day = (await db.scalars(select(models.WorkoutPlanDay).join(models.WorkoutPlanWeek).join(models.WorkoutPlan).where(
        models.WorkoutPlanDay.id == day_id, 
        models.WorkoutPlan.user_id == current_user.id
    ))).first()

    if not day:
        raise HTTPException(status_code=404, detail="Day not found or unauthorized access.")

    # Check if exercise exists
    exercise = (await db.scalars(select(models.Exercise).where(models.Exercise.exercise_id == exercise_data.exercise_id))).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found.")

    try:
        exercise_entry = models.WorkoutPlanExercise(
            workout_plan_day_id=day_id,
            exercise_id=exercise_data.exercise_id,
            sets=exercise_data.sets,
            reps=exercise_data.reps,
            order=exercise_data.order
        )
        db.add(exercise_entry)
        await db.commit()
        await db.refresh(exercise_entry)
        return exercise_entry

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding exercise: {str(e)}")



@workout_route.put("/{plan_id}", response_model=schemas.DisplayWorkoutPlan)
def update_workout_plan(
    plan_id: int, 
    update_data: schemas.UpdateWorkoutPlan, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id, models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found.")

    # Update fields only if provided
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    logger.info("Workout plan updated successfully")
    # Clear the cache for this plan
    cache_key = f"user:{current_user.id}:workout_plan:{plan_id}"
    cache.delete(cache_key)
    return plan


@workout_route.put("/days/{day_id}/exercises", response_model=List[schemas.DisplayWorkoutPlanExercise])
def update_exercises_in_day(
    day_id: int, 
    exercises: List[schemas.UpdateExerciseInWorkout], 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    day = db.query(models.WorkoutPlanDay).join(models.WorkoutPlanWeek).join(models.WorkoutPlan).filter(
        models.WorkoutPlanDay.id == day_id, models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not day:
        raise HTTPException(status_code=404, detail="Day not found.")

    updated_exercises = []
    for exercise in exercises:
        workout_exercise = db.query(models.WorkoutPlanExercise).filter(
            models.WorkoutPlanExercise.workout_plan_day_id == day_id,
            models.WorkoutPlanExercise.exercise_id == exercise.exercise_id
        ).first()

        if not workout_exercise:
            raise HTTPException(status_code=404, detail=f"Exercise {exercise.exercise_id} not found in this day.")

        # Only update provided fields
        for key,value in updated_exercises.model_dump(exclude_unset=True).items():
            setattr(workout_exercise, key, value)

        updated_exercises.append(workout_exercise)

    db.commit() 
    db.refresh(updated_exercises)
    logger.info("Exercises updated successfully")
    # Clear the cache for this day's exercises
    cache_key = f"user:{current_user.id}:workout_day_exercises:{day_id}"
    cache.delete(cache_key)
    return updated_exercises





@workout_route.delete("/{plan_id}", status_code=204)
async def delete_workout_plan(plan_id: int, db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # plan = db.query(models.WorkoutPlan).filter(
    #     models.WorkoutPlan.id == plan_id, models.WorkoutPlan.user_id == current_user.id
    # ).first()
    try:
        plan = (await db.scalars(select(models.WorkoutPlan).where(
            models.WorkoutPlan.id == plan_id, 
            models.WorkoutPlan.user_id == current_user.id
        ))).first()
        if not plan:
            raise HTTPException(status_code=404, detail="Workout plan not found.")

        await db.delete(plan)
        await db.commit()
        logger.info("Workout plan deleted successfully")
        # Clear the cache for this plan
        plan_cache_key = f"user:{current_user.id}:workout_plan:{plan_id}"
        wokrout_list_cache_key = f"user:{current_user.id}:workouts"
        cache.delete(plan_cache_key)
        cache.delete(wokrout_list_cache_key)
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.delete("/days/{day_id}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_from_day(
    day_id: int, 
    exercise_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    exercise = db.query(models.WorkoutPlanExercise).join(models.WorkoutPlanDay).join(models.WorkoutPlanWeek).join(models.WorkoutPlan).filter(
        models.WorkoutPlanExercise.workout_plan_day_id == day_id, 
        models.WorkoutPlanExercise.exercise_id == exercise_id, 
        models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found.")

    db.delete(exercise)
    db.commit()
    logger.info("Exercise deleted successfully")
    # Clear the cache for this day's exercises
    cache_key = f"user:{current_user.id}:workout_day_exercises:{day_id}"
    cache.delete(cache_key)
