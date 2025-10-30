"""merge heads

Revision ID: c32802adbe82
Revises: 5c3726c5c481, 9b4a283fbe0a
Create Date: 2025-10-13 13:49:31.820911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c32802adbe82'
down_revision: Union[str, None] = ('5c3726c5c481', '9b4a283fbe0a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
