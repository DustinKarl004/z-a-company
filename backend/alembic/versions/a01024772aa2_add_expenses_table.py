"""add expenses table

Revision ID: a01024772aa2
Revises: f1a2b3c4d5e6
Create Date: 2026-07-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a01024772aa2'
down_revision: Union[str, None] = 'f1a2b3c4d5e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('expenses',
    sa.Column('branch_id', sa.String(length=12), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('created_by_id', sa.String(length=12), nullable=False),
    sa.Column('id', sa.String(length=12), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ),
    sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('expenses')
