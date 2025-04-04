"""updated workout plan exercise model

Revision ID: df444e225f28
Revises: 39e8df8de138
Create Date: 2025-03-01 11:32:14.056609

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df444e225f28'
down_revision: Union[str, None] = '39e8df8de138'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('workout_plan_exercises_workout_plan_id_fkey', 'workout_plan_exercises', type_='foreignkey')
    op.drop_column('workout_plan_exercises', 'workout_plan_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('workout_plan_exercises', sa.Column('workout_plan_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('workout_plan_exercises_workout_plan_id_fkey', 'workout_plan_exercises', 'workout_plans', ['workout_plan_id'], ['id'])
    # ### end Alembic commands ###
