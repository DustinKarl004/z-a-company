from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.stock_delivery import StockDelivery


def create_delivery(
    db: Session,
    *,
    branch_id: str,
    item_id: str,
    date_: date,
    quantity_delivered: float,
    created_by_id: str,
) -> StockDelivery:
    delivery = StockDelivery(
        branch_id=branch_id,
        item_id=item_id,
        date=date_,
        quantity_delivered=quantity_delivered,
        created_by_id=created_by_id,
    )
    db.add(delivery)
    db.commit()
    db.refresh(delivery)
    return delivery


def get_delivery_for_day(
    db: Session, *, branch_id: str, item_id: str, date_: date
) -> StockDelivery | None:
    return db.scalar(
        select(StockDelivery).where(
            StockDelivery.branch_id == branch_id,
            StockDelivery.item_id == item_id,
            StockDelivery.date == date_,
        )
    )


def list_deliveries(
    db: Session,
    *,
    branch_id: str | None = None,
    date_: date | None = None,
) -> list[StockDelivery]:
    stmt = select(StockDelivery)
    if branch_id:
        stmt = stmt.where(StockDelivery.branch_id == branch_id)
    if date_:
        stmt = stmt.where(StockDelivery.date == date_)
    return list(db.scalars(stmt.order_by(StockDelivery.date.desc())))


def get_delivery(db: Session, delivery_id: str) -> StockDelivery | None:
    return db.get(StockDelivery, delivery_id)


def update_delivery(db: Session, delivery: StockDelivery, *, quantity_delivered: float | None) -> StockDelivery:
    if quantity_delivered is not None:
        delivery.quantity_delivered = quantity_delivered
    db.commit()
    db.refresh(delivery)
    return delivery


def reassign_date(db: Session, delivery: StockDelivery, *, date_: date) -> StockDelivery:
    delivery.date = date_
    db.commit()
    db.refresh(delivery)
    return delivery


def delete_delivery(db: Session, delivery: StockDelivery) -> None:
    db.delete(delivery)
    db.commit()
