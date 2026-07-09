"""make expenses.amount nullable so a day's bill can be explicitly cleared

Revision ID: c4d5e6f7a8b9
Revises: b3c4d5e6f7a8
Create Date: 2026-07-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'c4d5e6f7a8b9'
down_revision: Union[str, None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('expenses') as batch_op:
        batch_op.alter_column('amount', existing_type=sa.Float(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('expenses') as batch_op:
        batch_op.alter_column('amount', existing_type=sa.Float(), nullable=False)
