from sqlalchemy import Boolean, Column, Date, Float, Integer, String, ForeignKey, DATE, BigInteger, TIMESTAMP, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base

class UserProfile(Base):
    __tablename__ = 'user_profile'
    
    id = Column(Integer, primary_key=True, index=True)
    # Remove ForeignKey constraint, just use UUID column
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    first_name = Column(String, nullable=False, index=True)
    last_name = Column(String)
    date_of_birth = Column(DATE, nullable=False)
    gender = Column(String, nullable=False, default='Not Specified')
    height = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    fitness_goal = Column(String)
    fitness_level = Column(String)
    available_time = Column(Integer)
    country_code = Column(String, nullable=False)
    contact_number = Column(BigInteger, nullable=False, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())

class Exercise(Base):
    __tablename__ = "exercise"
    
    exercise_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    muscle_group = Column(String, nullable=True)
    category = Column(String, nullable=True)
    difficulty_level = Column(String, nullable=True)
    equipment_needed = Column(Boolean, nullable=False, default=False)
    equipment_details = Column(String, nullable=True)
    calories_burnt_per_minute = Column(Float, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())
    
    workout_plans = relationship("WorkoutPlanExercise", back_populates="exercise")

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    # Remove ForeignKey constraint, just use UUID column
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    weeks = Column(Integer, nullable=False, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    weeks_schedule = relationship("WorkoutPlanWeek", back_populates="workout_plan", cascade="all, delete-orphan")
    workout_logs = relationship("WorkoutLog", back_populates="workout_plan", cascade="all, delete-orphan")


class WorkoutPlanWeek(Base):
    __tablename__ = "workout_plan_weeks"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False)
    week_number = Column(Integer, nullable=False)
    
    workout_plan = relationship("WorkoutPlan", back_populates="weeks_schedule")
    days_schedule = relationship("WorkoutPlanDay", back_populates="week", cascade="all, delete-orphan")

class WorkoutPlanDay(Base):
    __tablename__ = "workout_plan_days"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_plan_week_id = Column(Integer, ForeignKey("workout_plan_weeks.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String, nullable=False)
    
    week = relationship("WorkoutPlanWeek", back_populates="days_schedule")
    exercises = relationship("WorkoutPlanExercise", back_populates="day", cascade="all, delete-orphan")

class WorkoutPlanExercise(Base):
    __tablename__ = "workout_plan_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercise.exercise_id",ondelete="CASCADE"), nullable=False)
    workout_plan_day_id = Column(Integer, ForeignKey("workout_plan_days.id", ondelete="CASCADE"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)
    
    day = relationship("WorkoutPlanDay", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_plans")

class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    # Remove ForeignKey constraint, just use UUID column
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id",ondelete="CASCADE"), nullable=False)
    date = Column(TIMESTAMP, server_default=func.now())
    status = Column(String, server_default="completed")
    duration = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    workout_plan = relationship("WorkoutPlan", back_populates="workout_logs")
    exercises = relationship("WorkoutLogExercise", back_populates="workout_log", cascade="all, delete-orphan")

class WorkoutLogExercise(Base):
    __tablename__ = "workout_log_exercises"
    
    id = Column(Integer, primary_key=True, index=True)
    workout_log_id = Column(Integer, ForeignKey("workout_logs.id",ondelete="CASCADE"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.exercise_id",ondelete="CASCADE"), nullable=False)
    sets_completed = Column(Integer, nullable=True)
    reps_completed = Column(Integer, nullable=True)
    weight_used = Column(Float, nullable=True)

    workout_log = relationship("WorkoutLog", back_populates="exercises")

class Progress(Base):
    __tablename__ = "progress"
    
    id = Column(Integer, primary_key=True, index=True)
    # Remove ForeignKey constraint, just use UUID column
    user_id = Column(UUID(as_uuid=True), nullable=False,index=True)
    
    date = Column(Date, nullable=False)
    weight = Column(Float, nullable=False)
    bmi = Column(Float, nullable=True)
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
