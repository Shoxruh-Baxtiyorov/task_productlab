"""empty message

Revision ID: 6d168c714485
Revises: 51e51405a4c7
Create Date: 2024-01-01 17:21:55.937835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6d168c714485'
down_revision: Union[str, None] = '51e51405a4c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE taskstatustype ADD VALUE 'SUBMITTED';")


def downgrade() -> None:
    op.execute('ALTER TYPE taskstatustype RENAME TO taskstatustype_old;')
    op.execute("CREATE TYPE taskstatustype as ENUM ('ATWORK', 'ACCEPTSOFFERS', 'ARCHIVED', 'COMPLETED', 'CANCELLED');")
    op.execute('ALTER TABLE tasks ALTER COLUMN status TYPE taskstatustype USING taskstatustype::text::taskstatustype;')
    op.execute('DROP TYPE taskstatustype_old')
