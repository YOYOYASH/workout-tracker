from sqlalchemy import Boolean, Column, Date, Float, Integer, String, ForeignKey, DATE,BigInteger,TIMESTAMP, Text, func
from sqlalchemy.orm import relationship
from db.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True, index = True)
    username = Column(String,index=True,nullable=False)
    email = Column(String,index=True,unique=True,nullable=False)
    password = Column(String,nullable=False)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    workout_plans = relationship("WorkoutPlan", back_populates="current_user")
    workout_logs = relationship("WorkoutLog", back_populates="user")
    progress = relationship("Progress", back_populates="user", cascade="all, delete-orphan")
    

class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String,nullable=False,index=True)
    last_name = Column(String)
    date_of_birth = Column(DATE,nullable=False)
    gender = Column(String,nullable=False,default='Not Specified')
    height = Column(Integer,nullable=False)
    weight = Column(Integer,nullable=False)
    fitness_goal = Column(String)  # Fitness goal, e.g., 'weight loss'
    fitness_level = Column(String)  # Fitness level, e.g., 'beginner'
    available_time = Column(Integer)  # Time available for workouts in minutes
    contact_number = Column(BigInteger,nullable=False,unique=True,index=True)
    created_at = Column(TIMESTAMP,nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP,nullable=False,server_default=func.now(), onupdate=func.now())


    user = relationship("User", back_populates="profile")
    

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

    def __repr__(self):
        return f"<Exercise(name={self.name}, muscle_group={self.muscle_group})>"

class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    weeks = Column(Integer, nullable=False,default=1) 
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    current_user = relationship("User", back_populates="workout_plans")
    weeks_schedule = relationship("WorkoutPlanWeek", back_populates="workout_plan", cascade="all, delete-orphan")


class WorkoutPlanWeek(Base):
    __tablename__ = "workout_plan_weeks"

    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id", ondelete="CASCADE"), nullable=False)
    week_number = Column(Integer, nullable=False)  # Week 1, Week 2, etc.

    # Relationships
    workout_plan = relationship("WorkoutPlan", back_populates="weeks_schedule")
    days_schedule = relationship("WorkoutPlanDay", back_populates="week", cascade="all, delete-orphan")

class WorkoutPlanDay(Base):
    __tablename__ = "workout_plan_days"

    id = Column(Integer, primary_key=True, index=True)
    workout_plan_week_id = Column(Integer, ForeignKey("workout_plan_weeks.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String, nullable=False)  # e.g., "Monday", "Wednesday"

    # Relationships
    week = relationship("WorkoutPlanWeek", back_populates="days_schedule")
    exercises = relationship("WorkoutPlanExercise", back_populates="day", cascade="all, delete-orphan")


class WorkoutPlanExercise(Base):
    __tablename__ = "workout_plan_exercises"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercise.exercise_id"), nullable=False)
    workout_plan_day_id = Column(Integer, ForeignKey("workout_plan_days.id", ondelete="CASCADE"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)

    # Relationships
    day = relationship("WorkoutPlanDay", back_populates="exercises")
    exercise = relationship("Exercise", back_populates="workout_plans")



class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"), nullable=False)
    date = Column(TIMESTAMP, server_default=func.now())
    status = Column(String, server_default="completed")  # Completed, skipped, partial
    duration = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    user = relationship("User", back_populates="workout_logs")
    workout_plan = relationship("WorkoutPlan")


class WorkoutLogExercise(Base):
    __tablename__ = "workout_log_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_log_id = Column(Integer, ForeignKey("workout_logs.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.exercise_id"), nullable=False)
    sets_completed = Column(Integer, nullable=True)
    reps_completed = Column(Integer, nullable=True)
    weight_used = Column(Float, nullable=True)  # Track weight used


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)  # The date the progress was logged
    weight = Column(Float, nullable=False)  # Weight in kg
    bmi = Column(Float, nullable=True)  # Calculated BMI (optional)
    body_fat_percentage = Column(Float, nullable=True)  # Body fat percentage (optional)
    muscle_mass = Column(Float, nullable=True)  # Muscle mass (optional)
    notes = Column(String, nullable=True)  # Any additional notes

    # Relationship with User
    user = relationship("User", back_populates="progress")