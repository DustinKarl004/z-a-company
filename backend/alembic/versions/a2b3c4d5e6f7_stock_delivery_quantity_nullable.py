"""make stock_deliveries.quantity_delivered nullable for need-only flags

Revision ID: a2b3c4d5e6f7
Revises: c3d5e7f9a1b3
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a2b3c4d5e6f7'
down_revision: Union[str, None] = 'c3d5e7f9a1b3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('stock_deliveries') as batch_op:
        batch_op.alter_column('quantity_delivered', existing_type=sa.Float(), nullable=True)


def downgrade() -> None:
    op.execute('UPDATE stock_deliveries SET quantity_delivered = 0 WHERE quantity_delivered IS NULL')
    with op.batch_alter_table('stock_deliveries') as batch_op:
        batch_op.alter_column('quantity_delivered', existing_type=sa.Float(), nullable=False)
