from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock_need import StockNeed


def create_need(
    db: Session,
    *,
    branch_id: str,
    item_id: str,
    date_: date,
    created_by_id: str,
) -> StockNeed:
    need = StockNeed(
        branch_id=branch_id,
        item_id=item_id,
        date=date_,
        created_by_id=created_by_id,
    )
    db.add(need)
    db.commit()
    db.refresh(need)
    return need


def get_need_for_day(db: Session, *, branch_id: str, item_id: str, date_: date) -> StockNeed | None:
    return db.scalar(
        select(StockNeed).where(
            StockNeed.branch_id == branch_id,
            StockNeed.item_id == item_id,
            StockNeed.date == date_,
        )
    )


def get_need(db: Session, need_id: str) -> StockNeed | None:
    return db.get(StockNeed, need_id)


def list_needs(
    db: Session, *, branch_id: str | None = None, date_: date | None = None, is_delivered: bool | None = None
) -> list[StockNeed]:
    stmt = select(StockNeed)
    if branch_id:
        stmt = stmt.where(StockNeed.branch_id == branch_id)
    if date_:
        stmt = stmt.where(StockNeed.date == date_)
    if is_delivered is not None:
        stmt = stmt.where(StockNeed.is_delivered.is_(is_delivered))
    return list(db.scalars(stmt.order_by(StockNeed.date.desc())))


def update_need(db: Session, need: StockNeed, *, is_delivered: bool) -> StockNeed:
    need.is_delivered = is_delivered
    db.commit()
    db.refresh(need)
    return need


def delete_need(db: Session, need: StockNeed) -> None:
    db.delete(need)
    db.commit()
