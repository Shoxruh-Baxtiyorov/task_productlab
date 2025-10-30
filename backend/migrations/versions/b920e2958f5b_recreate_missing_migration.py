"""recreate_missing_migration

Revision ID: b920e2958f5b
Revises: e919d647e95d
Create Date: 2025-08-13 21:46:13.526661

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b920e2958f5b'
down_revision: Union[str, None] = 'e919d647e95d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
