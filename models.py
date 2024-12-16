from sqlalchemy import Column, Integer, String, ForeignKey, DATE,BigInteger,TIMESTAMP, func
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
    



