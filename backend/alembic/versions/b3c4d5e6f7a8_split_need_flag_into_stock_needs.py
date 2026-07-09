"""decouple the "need delivery" flag from stock_deliveries into its own stock_needs table

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-07-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.core.ids import generate_id


revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, None] = 'a2b3c4d5e6f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'stock_needs',
        sa.Column('id', sa.String(length=12), primary_key=True),
        sa.Column('branch_id', sa.String(length=12), sa.ForeignKey('branches.id'), nullable=False),
        sa.Column('item_id', sa.String(length=12), sa.ForeignKey('stock_items.id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('is_delivered', sa.Boolean(), nullable=False),
        sa.Column('created_by_id', sa.String(length=12), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    bind = op.get_bind()
    deliveries = sa.table(
        'stock_deliveries',
        sa.column('id', sa.String),
        sa.column('branch_id', sa.String),
        sa.column('item_id', sa.String),
        sa.column('date', sa.Date),
        sa.column('quantity_delivered', sa.Float),
        sa.column('is_short', sa.Boolean),
        sa.column('is_delivered', sa.Boolean),
        sa.column('created_by_id', sa.String),
        sa.column('created_at', sa.DateTime),
    )
    needs = sa.table(
        'stock_needs',
        sa.column('id', sa.String),
        sa.column('branch_id', sa.String),
        sa.column('item_id', sa.String),
        sa.column('date', sa.Date),
        sa.column('is_delivered', sa.Boolean),
        sa.column('created_by_id', sa.String),
        sa.column('created_at', sa.DateTime),
    )

    flagged = bind.execute(
        sa.select(
            deliveries.c.id,
            deliveries.c.branch_id,
            deliveries.c.item_id,
            deliveries.c.date,
            deliveries.c.quantity_delivered,
            deliveries.c.is_delivered,
            deliveries.c.created_by_id,
            deliveries.c.created_at,
        ).where(deliveries.c.is_short.is_(True))
    ).fetchall()

    empty_delivery_ids = []
    for row in flagged:
        bind.execute(
            needs.insert().values(
                id=generate_id(),
                branch_id=row.branch_id,
                item_id=row.item_id,
                date=row.date,
                is_delivered=row.is_delivered,
                created_by_id=row.created_by_id,
                created_at=row.created_at,
            )
        )
        if row.quantity_delivered is None:
            empty_delivery_ids.append(row.id)

    if empty_delivery_ids:
        bind.execute(deliveries.delete().where(deliveries.c.id.in_(empty_delivery_ids)))

    with op.batch_alter_table('stock_deliveries') as batch_op:
        batch_op.alter_column('quantity_delivered', existing_type=sa.Float(), nullable=False)
        batch_op.drop_column('is_short')
        batch_op.drop_column('is_delivered')


def downgrade() -> None:
    with op.batch_alter_table('stock_deliveries') as batch_op:
        batch_op.add_column(sa.Column('is_short', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column('is_delivered', sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.alter_column('quantity_delivered', existing_type=sa.Float(), nullable=True)

    op.drop_table('stock_needs')
