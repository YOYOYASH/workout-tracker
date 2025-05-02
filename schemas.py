from pydantic import  BaseModel, EmailStr
from datetime import date,datetime
from typing import Optional

class UserBase(BaseModel):
    username:str
    email: EmailStr
    password:str

class CreateUser(UserBase):
    pass

class DisplayUser(BaseModel):
    id:int
    username: str
    email:str

    class Config:
        from_attributes = True

class UpdateUser(BaseModel):
    email:EmailStr


class UserProfile(BaseModel):
    first_name:str
    last_name:Optional[str]=None
    date_of_birth:date
    height:int
    weight:int
    fitness_goal:Optional[str]=None
    fitness_level:Optional[str]='beginner'
    available_time:Optional[int] = None
    contact_number:int

class DisplayUserProfile(UserProfile):
    id:int
    user_id:int
    class Config:
        from_attributes = True

class UpdateUserProfile(BaseModel):
    first_name:Optional[str]=None
    last_name:Optional[str]=None
    date_of_birth:Optional[date]=None
    height:Optional[int]=None
    weight:Optional[int]=None
    fitness_goal:Optional[str]=None
    fitness_level:Optional[str]=None
    available_time:Optional[int] = None
    contact_number:Optional[int]=None


class TokenData(BaseModel):
    token:str
    type:str


#------------------------------Exercise Schema--------------------------------

class ExerciseBase(BaseModel):
    name:str
    description:Optional[str]=None
    muscle_group:Optional[str]=None
    category:Optional[str]=None
    difficulty_level:Optional[str]=None
    equipment_needed:Optional[bool]=False
    equipment_details:Optional[str]=None
    calories_burnt_per_minute:Optional[float]=None

class CreateExercise(ExerciseBase):
    pass

class DisplayExercise(BaseModel):
    exercise_id:int
    name:str
    description:Optional[str]=None
    muscle_group:Optional[str]=None
    category:Optional[str]=None
    difficulty_level:Optional[str]=None
    equipment_needed:Optional[bool]=False
    equipment_details:Optional[str]=None
    calories_burnt_per_minute:Optional[float]=None
    created_at:datetime
    updated_at:datetime

    class Config:
        from_attributes = True


#------------------------------Workout Plan Schema--------------------------------


class CreateWorkoutPlan(BaseModel):
    name:str
    description:Optional[str]=None
    weeks:Optional[int]=None

class DisplayWorkoutPlan(BaseModel):
    id:int
    user_id:int
    name:str
    description:Optional[str]=None
    created_at:datetime
    updated_at:datetime

    class Config:
        from_attributes = True

class UpdateWorkoutPlan(BaseModel):
    name:Optional[str]=None
    description:Optional[str]=None

class CreateWeek(BaseModel):
    week_number:int

class DisplayWeek(CreateWeek):
    id:int

class CreateWorkoutDay(BaseModel):
    day_of_week:str

class DisplayWorkoutDay(CreateWorkoutDay):
    id:int

class AddExerciseToWorkout(BaseModel):
    exercise_id:int
    workout_plan_day_id:int
    sets:int
    reps:int
    order:int

class UpdateExerciseInWorkout(BaseModel):
    exercise_id:int
    sets:Optional[int]=None
    reps:Optional[int]=None
    order:Optional[int]=None

class DisplayWorkoutPlanExercise(BaseModel):
    id:int
    workout_plan_day_id:int
    exercise_id:int
    sets:int
    reps:int
    order:int

    class Config:
        from_attributes = True
    


#------------------------------Workout log Schema--------------------------------

class CreateWorkoutLog(BaseModel):
    workout_plan_id:int
    duration:int
    notes:Optional[str]=None

class DisplayWorkoutLog(CreateWorkoutLog):
    date:datetime
    id:int

class AddExerciseToWorkoutLog(BaseModel):
    exercise_id:int
    sets_completed:int
    reps_completed:int
    weight_used:Optional[float]=None

class DisplayWorkoutLogExercise(AddExerciseToWorkoutLog):
    id:int
    workout_log_id:int

    class Config:
        from_attributes = True


#------------------------------User Progress Schema--------------------------------

class CreateProgress(BaseModel):
    date:datetime
    weight:float
    bmi:Optional[float]=None
    body_fat_percentage:Optional[float]=None
    muscle_mass:Optional[float]=None
    notes:Optional[str]=None

class DisplayProgress(CreateProgress):
    id: int
    user_id:int

    class Config:
        from_attributes = True