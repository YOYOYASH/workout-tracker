from sqlalchemy import Boolean, Column, Float, Integer, String, ForeignKey, DATE,BigInteger,TIMESTAMP, Text, func
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
    

class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String,nullable=False,index=True)
    last_name = Column(String)
    date_of_birth = Column(DATE,nullable=False)
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
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    current_user = relationship("User", back_populates="workout_plans")
    exercises = relationship("WorkoutPlanExercise", back_populates="workout_plan")

    


class WorkoutPlanExercise(Base):
    __tablename__ = "workout_plan_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_plan_id = Column(Integer, ForeignKey("workout_plans.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercise.exercise_id"), nullable=False)
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)

    # Relationships
    workout_plan = relationship("WorkoutPlan", back_populates="exercises")
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

