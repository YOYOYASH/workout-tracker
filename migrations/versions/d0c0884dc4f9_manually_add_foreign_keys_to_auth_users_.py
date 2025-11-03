"""Manually add foreign keys to auth users table

Revision ID: d0c0884dc4f9
Revises: db12c0d13f2a
Create Date: 2025-07-24 17:14:01.174938

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0c0884dc4f9'
down_revision: Union[str, None] = 'db12c0d13f2a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Manually creates foreign key constraints from local tables
    to the uid column in the supabase auth.users table.
    """
    # Foreign key for user_profile table
    op.create_foreign_key(
        'fk_user_profile_user_id_to_auth_users', # A unique constraint name
        'user_profile',                          # Source table
        'users',                                 # Referent (target) table
        ['user_id'],                             # Source column(s)
        ['id'],                                 # Referent column(s)
        referent_schema='auth',                  # Referent schema
        ondelete='CASCADE'
    )

    # Foreign key for workout_plans table
    op.create_foreign_key(
        'fk_workout_plans_user_id_to_auth_users',
        'workout_plans',
        'users',
        ['user_id'],
        ['id'],
        referent_schema='auth',
        ondelete='CASCADE'
    )

    # Foreign key for workout_logs table
    op.create_foreign_key(
        'fk_workout_logs_user_id_to_auth_users',
        'workout_logs',
        'users',
        ['user_id'],
        ['id'],
        referent_schema='auth',
        ondelete='CASCADE'
    )

    # Foreign key for progress table
    op.create_foreign_key(
        'fk_progress_user_id_to_auth_users',
        'progress',
        'users',
        ['user_id'],
        ['id'],
        referent_schema='auth',
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """
    Removes the manually created foreign key constraints.
    """
    op.drop_constraint('fk_progress_user_id_to_auth_users', 'progress', type_='foreignkey')
    op.drop_constraint('fk_workout_logs_user_id_to_auth_users', 'workout_logs', type_='foreignkey')
    op.drop_constraint('fk_workout_plans_user_id_to_auth_users', 'workout_plans', type_='foreignkey')
    op.drop_constraint('fk_user_profile_user_id_to_auth_users', 'user_profile', type_='foreignkey')
