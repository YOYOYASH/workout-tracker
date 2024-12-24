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
    updated_at = Column(TIMESTAMP,nullable=False, server_default=func.now())

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
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    def __repr__(self):
        return f"<Exercise(name={self.name}, muscle_group={self.muscle_group})>"

    



