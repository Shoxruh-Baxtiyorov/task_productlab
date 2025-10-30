"""empty message

Revision ID: 7132850d751d
Revises: 26ccf2222873, a6c5d0efac01
Create Date: 2025-02-25 19:20:51.548405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7132850d751d'
down_revision: Union[str, None] = ('26ccf2222873', 'a6c5d0efac01')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
