"""add user backup codes

Revision ID: d4f2a6b8c9e1
Revises: c7c50237058c
Create Date: 2026-07-06 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd4f2a6b8c9e1'
down_revision: Union[str, None] = 'c7c50237058c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('backup_codes', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'backup_codes')
