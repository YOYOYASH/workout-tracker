from typing import List
from fastapi import APIRouter,HTTPException,status,Depends
from db.database import get_db
from sqlalchemy.orm import Session
import models
from oauth2 import get_current_user
from utils.logger import setup_logger
import schemas

workout_route = APIRouter(prefix='/workouts')
logger = setup_logger("workout_route")

@workout_route.get('/',response_model=List[schemas.DisplayWorkoutPlan])
def get_workouts(db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)) -> list:
    try:
        result = db.query(models.WorkoutPlan).all()
        if len(result) == 0:
            logger.warning(f"No workout plan found in database")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No workout plan found in database")
        logger.info("Workout plans fetched successfully")
        return result
    except HTTPException as http_exec:
        raise http_exec
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.get("/{plan_id}")
def get_workout_plan(
    plan_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id, models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found.")

    weeks = db.query(models.WorkoutPlanWeek).filter(models.WorkoutPlanWeek.workout_plan_id == plan_id).all()
    
    plan_data = {
        "id": plan.id,
        "name": plan.name,
        "description": plan.description,
        "weeks": plan.weeks,
        "schedule": []
    }

    for week in weeks:
        days = db.query(models.WorkoutPlanDay).filter(models.WorkoutPlanDay.workout_plan_week_id == week.id).all()
        week_data = {
            "week_number": week.week_number,
            "days": []
        }

        for day in days:
            week_data["days"].append({"id": day.id, "day_of_week": day.day_of_week})

        plan_data["schedule"].append(week_data)

    return plan_data

@workout_route.get("/days/{day_id}/exercises", response_model=List[schemas.DisplayWorkoutPlanExercise])
def get_exercises_in_day(
    day_id: int, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    day = db.query(models.WorkoutPlanDay).join(models.WorkoutPlanWeek).join(models.WorkoutPlan).filter(
        models.WorkoutPlanDay.id == day_id, 
        models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not day:
        raise HTTPException(status_code=404, detail="Day not found or unauthorized access.")

    exercises = db.query(models.WorkoutPlanExercise).filter(models.WorkoutPlanExercise.workout_plan_day_id == day_id).all()
    return exercises


@workout_route.post('/',status_code=status.HTTP_201_CREATED,response_model=schemas.DisplayWorkoutPlan)
def create_workout(workout_data: schemas.CreateWorkoutPlan,db:Session = Depends(get_db),current_user:dict = Depends(get_current_user)):
    try:
        new_workout = models.WorkoutPlan(user_id=current_user.id,**workout_data.model_dump())
        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)
        logger.info("Workout plan created successfully")
        return new_workout
    except Exception as e:
        logger.error(str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@workout_route.post("/{plan_id}/weeks", response_model=schemas.DisplayWeek)
def add_week_to_plan(
    plan_id: int, 
    week_data: schemas.CreateWeek, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    workout_plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id, models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not workout_plan:
        raise HTTPException(status_code=404, detail="Workout plan not found or unauthorized access.")
    
    if week_data.week_number < 1 or week_data.week_number > workout_plan.weeks:
        raise HTTPException(status_code=400, detail=f"Invalid week number. Must be between 1 and {workout_plan.weeks}.")

    # Prevent duplicate weeks
    existing_week = db.query(models.WorkoutPlanWeek).filter(
        models.WorkoutPlanWeek.workout_plan_id == plan_id,
        models.WorkoutPlanWeek.week_number == week_data.week_number
    ).first()

    if existing_week:
        raise HTTPException(status_code=400, detail=f"Week {week_data.week_number} already exists in this plan.")

    try:
        week = models.WorkoutPlanWeek(
            workout_plan_id=plan_id,
            week_number=week_data.week_number
        )
        db.add(week)
        db.commit()
        db.refresh(week)
        return week

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding week: {str(e)}")


@workout_route.post("/weeks/{week_id}/days", response_model=schemas.DisplayWorkoutDay)
def add_day_to_week(
    week_id: int, 
    day_data: schemas.CreateWorkoutDay, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    week = db.query(models.WorkoutPlanWeek).join(models.WorkoutPlan).filter(
        models.WorkoutPlanWeek.id == week_id, 
        models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not week:
        raise HTTPException(status_code=404, detail="Week not found or unauthorized access.")

    # Prevent duplicate days
    existing_day = db.query(models.WorkoutPlanDay).filter(
        models.WorkoutPlanDay.workout_plan_week_id == week_id,
        models.WorkoutPlanDay.day_of_week == day_data.day_of_week
    ).first()

    if existing_day:
        raise HTTPException(status_code=400, detail=f"{day_data.day_of_week} already exists in this week.")

    try:
        day = models.WorkoutPlanDay(
            workout_plan_week_id=week_id,
            day_of_week=day_data.day_of_week
        )
        db.add(day)
        db.commit()
        db.refresh(day)
        return day

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding day: {str(e)}")


@workout_route.post("/days/{day_id}/exercises", response_model=schemas.DisplayWorkoutPlanExercise)
def add_exercise_to_day(
    day_id: int, 
    exercise_data: schemas.AddExerciseToWorkout, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    day = db.query(models.WorkoutPlanDay).join(models.WorkoutPlanWeek).join(models.WorkoutPlan).filter(
        models.WorkoutPlanDay.id == day_id, 
        models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not day:
        raise HTTPException(status_code=404, detail="Day not found or unauthorized access.")

    # Check if exercise exists
    exercise = db.query(models.Exercise).filter(models.Exercise.exercise_id == exercise_data.exercise_id).first()
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
        db.commit()
        db.refresh(exercise_entry)
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
    return updated_exercises





@workout_route.delete("/{plan_id}", status_code=204)
def delete_workout_plan(plan_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    plan = db.query(models.WorkoutPlan).filter(
        models.WorkoutPlan.id == plan_id, models.WorkoutPlan.user_id == current_user.id
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="Workout plan not found.")

    db.delete(plan)
    db.commit()

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
