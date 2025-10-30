"""empty message

Revision ID: e94d07276d9e
Revises: 6d168c714485
Create Date: 2024-01-01 18:14:43.895216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e94d07276d9e'
down_revision: Union[str, None] = '6d168c714485'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_enum e
                    JOIN pg_type t ON t.oid = e.enumtypid
                    WHERE t.typname = 'taskeventtype' 
                    AND e.enumlabel = 'WORKACCEPTED'
                ) THEN
                    ALTER TYPE taskeventtype ADD VALUE 'WORKACCEPTED';
                END IF;
            END;
            $$;
        """)


def downgrade() -> None:
    op.execute('ALTER TYPE taskeventtype RENAME TO taskeventtype_old;')
    op.execute("CREATE TYPE taskeventtype AS ENUM ('ACCEPTOFFER', 'STARTWORK', 'SUBMITWORK', 'DEADLINESPENT', 'AUTOSCREENS', 'MESSAGE');")
    op.execute('ALTER TABLE task_events ALTER COLUMN event_type TYPE taskeventtype USING taskeventtype::text::taskeventtype;')
    op.execute('DROP TYPE taskeventtype_old;')
