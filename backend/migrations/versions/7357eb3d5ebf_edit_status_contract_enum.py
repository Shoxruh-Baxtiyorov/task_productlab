from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7357eb3d5ebf'
down_revision = '36963a2a105e'
branch_labels = None
depends_on = None


# Определяем новое перечисление с добавленным значением
new_enum = postgresql.ENUM('ATWORK', 'COMPLETED', 'CANCELLED', 'INSPECTED', name='contractstatustype')
old_enum = postgresql.ENUM('ATWORK', 'COMPLETED', 'CANCELLED', name='contractstatustype')

def upgrade():
    # Обновляем существующий ENUM, добавляя новое значение
    op.execute("ALTER TYPE contractstatustype ADD VALUE 'INSPECTED'")


def downgrade():
    # В случае отката миграции, создаем новый ENUM без "INSPECTED"
    op.execute("ALTER TABLE contracts ALTER COLUMN status TYPE TEXT")  # Временно меняем тип
    old_enum.create(op.get_bind(), checkfirst=True)
    op.execute("ALTER TABLE contracts ALTER COLUMN status TYPE contractstatustype USING status::contractstatustype")
    op.execute("DROP TYPE contractstatustype")
