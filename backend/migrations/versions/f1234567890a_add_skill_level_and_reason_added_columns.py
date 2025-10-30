"""add skill_level and reason_added columns

Revision ID: f1234567890a
Revises: 871768e0ff52
Create Date: 2025-10-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'f1234567890a'
down_revision: Union[str, None] = '871768e0ff52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    skill_level_enum = postgresql.ENUM('WANT', 'WILL', 'IN', name='skillleveltype', create_type=False)
    user_segment_reason_enum = postgresql.ENUM(
        'USER_SKILLS', 'USER_BIO_DESCRIPTIONS', 'USER_SUBSCRIBED', 'USER_RESUME', 'TASK_OFFER',
        name='usersegmentreasontype',
        create_type=False
    )
    subscription_reason_enum = postgresql.ENUM(
        'USER_SUBSCRIBED', 'USER_RESUME', 'TASK_OFFER',
        name='subscriptionreasontype',
        create_type=False
    )
    
    # Create the enum types in the database
    skill_level_enum.create(op.get_bind(), checkfirst=True)
    user_segment_reason_enum.create(op.get_bind(), checkfirst=True)
    subscription_reason_enum.create(op.get_bind(), checkfirst=True)
    
    # Add columns to user_segments
    op.add_column('user_segments', sa.Column('skill_level', skill_level_enum, nullable=True))
    op.add_column('user_segments', sa.Column('reason_added', user_segment_reason_enum, nullable=True))
    
    # Add column to subscriptions
    op.add_column('subscriptions', sa.Column('reason_added', subscription_reason_enum, nullable=True))
    
    # Set default values for existing records in user_segments
    # Set reason_added based on fromme field
    op.execute("""
        UPDATE user_segments
        SET reason_added = CASE
            WHEN fromme = TRUE THEN 'USER_RESUME'::usersegmentreasontype
            ELSE 'USER_SUBSCRIBED'::usersegmentreasontype
        END
        WHERE reason_added IS NULL
    """)
    
    # Calculate and set skill_level based on claimed_tasks and completed_tasks
    op.execute("""
        UPDATE user_segments
        SET skill_level = CASE
            WHEN completed_tasks >= 3 THEN 'IN'::skillleveltype
            WHEN claimed_tasks > 0 AND completed_tasks < 3 THEN 'WILL'::skillleveltype
            WHEN claimed_tasks = 0 AND completed_tasks = 0 THEN 'WANT'::skillleveltype
            ELSE 'WANT'::skillleveltype
        END
        WHERE skill_level IS NULL
    """)
    
    # Set default values for existing records in subscriptions
    op.execute("""
        UPDATE subscriptions
        SET reason_added = CASE
            WHEN fromme = TRUE THEN 'USER_RESUME'::subscriptionreasontype
            ELSE 'USER_SUBSCRIBED'::subscriptionreasontype
        END
        WHERE reason_added IS NULL
    """)


def downgrade() -> None:
    # Drop columns
    op.drop_column('subscriptions', 'reason_added')
    op.drop_column('user_segments', 'reason_added')
    op.drop_column('user_segments', 'skill_level')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS subscriptionreasontype')
    op.execute('DROP TYPE IF EXISTS usersegmentreasontype')
    op.execute('DROP TYPE IF EXISTS skillleveltype')
