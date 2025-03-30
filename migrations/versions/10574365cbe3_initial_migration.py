"""initial migration

Revision ID: 10574365cbe3
Revises: 
Create Date: 2025-03-30 17:55:28.576238

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '10574365cbe3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('exercise',
    sa.Column('exercise_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('muscle_group', sa.String(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('difficulty_level', sa.String(), nullable=True),
    sa.Column('equipment_needed', sa.Boolean(), nullable=False),
    sa.Column('equipment_details', sa.String(), nullable=True),
    sa.Column('calories_burnt_per_minute', sa.Float(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('exercise_id')
    )
    op.create_index(op.f('ix_exercise_exercise_id'), 'exercise', ['exercise_id'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('password', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_table('progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.Column('bmi', sa.Float(), nullable=True),
    sa.Column('body_fat_percentage', sa.Float(), nullable=True),
    sa.Column('muscle_mass', sa.Float(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_progress_id'), 'progress', ['id'], unique=False)
    op.create_table('user_profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('date_of_birth', sa.DATE(), nullable=False),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('height', sa.Integer(), nullable=False),
    sa.Column('weight', sa.Integer(), nullable=False),
    sa.Column('fitness_goal', sa.String(), nullable=True),
    sa.Column('fitness_level', sa.String(), nullable=True),
    sa.Column('available_time', sa.Integer(), nullable=True),
    sa.Column('contact_number', sa.BigInteger(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    op.create_index(op.f('ix_user_profile_contact_number'), 'user_profile', ['contact_number'], unique=True)
    op.create_index(op.f('ix_user_profile_first_name'), 'user_profile', ['first_name'], unique=False)
    op.create_index(op.f('ix_user_profile_id'), 'user_profile', ['id'], unique=False)
    op.create_table('workout_plans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('weeks', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_plans_id'), 'workout_plans', ['id'], unique=False)
    op.create_table('workout_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('workout_plan_id', sa.Integer(), nullable=False),
    sa.Column('date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('status', sa.String(), server_default='completed', nullable=True),
    sa.Column('duration', sa.Integer(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['workout_plan_id'], ['workout_plans.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_logs_id'), 'workout_logs', ['id'], unique=False)
    op.create_table('workout_plan_weeks',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workout_plan_id', sa.Integer(), nullable=False),
    sa.Column('week_number', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['workout_plan_id'], ['workout_plans.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_plan_weeks_id'), 'workout_plan_weeks', ['id'], unique=False)
    op.create_table('workout_log_exercises',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workout_log_id', sa.Integer(), nullable=False),
    sa.Column('exercise_id', sa.Integer(), nullable=False),
    sa.Column('sets_completed', sa.Integer(), nullable=True),
    sa.Column('reps_completed', sa.Integer(), nullable=True),
    sa.Column('weight_used', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['exercise_id'], ['exercise.exercise_id'], ),
    sa.ForeignKeyConstraint(['workout_log_id'], ['workout_logs.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_log_exercises_id'), 'workout_log_exercises', ['id'], unique=False)
    op.create_table('workout_plan_days',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workout_plan_week_id', sa.Integer(), nullable=False),
    sa.Column('day_of_week', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['workout_plan_week_id'], ['workout_plan_weeks.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_plan_days_id'), 'workout_plan_days', ['id'], unique=False)
    op.create_table('workout_plan_exercises',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('exercise_id', sa.Integer(), nullable=False),
    sa.Column('workout_plan_day_id', sa.Integer(), nullable=False),
    sa.Column('sets', sa.Integer(), nullable=False),
    sa.Column('reps', sa.Integer(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['exercise_id'], ['exercise.exercise_id'], ),
    sa.ForeignKeyConstraint(['workout_plan_day_id'], ['workout_plan_days.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workout_plan_exercises_id'), 'workout_plan_exercises', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_workout_plan_exercises_id'), table_name='workout_plan_exercises')
    op.drop_table('workout_plan_exercises')
    op.drop_index(op.f('ix_workout_plan_days_id'), table_name='workout_plan_days')
    op.drop_table('workout_plan_days')
    op.drop_index(op.f('ix_workout_log_exercises_id'), table_name='workout_log_exercises')
    op.drop_table('workout_log_exercises')
    op.drop_index(op.f('ix_workout_plan_weeks_id'), table_name='workout_plan_weeks')
    op.drop_table('workout_plan_weeks')
    op.drop_index(op.f('ix_workout_logs_id'), table_name='workout_logs')
    op.drop_table('workout_logs')
    op.drop_index(op.f('ix_workout_plans_id'), table_name='workout_plans')
    op.drop_table('workout_plans')
    op.drop_index(op.f('ix_user_profile_id'), table_name='user_profile')
    op.drop_index(op.f('ix_user_profile_first_name'), table_name='user_profile')
    op.drop_index(op.f('ix_user_profile_contact_number'), table_name='user_profile')
    op.drop_table('user_profile')
    op.drop_index(op.f('ix_progress_id'), table_name='progress')
    op.drop_table('progress')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_exercise_exercise_id'), table_name='exercise')
    op.drop_table('exercise')
    # ### end Alembic commands ###
