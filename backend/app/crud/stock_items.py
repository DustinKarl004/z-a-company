from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.sale import Sale
from app.models.stock_count import StockCount
from app.models.stock_delivery import StockDelivery
from app.models.stock_item import StockItem


def create_stock_item(
    db: Session, *, name: str, unit: str, price: float = 0.0, category: str | None = None
) -> StockItem:
    item = StockItem(name=name, unit=unit, price=price, category=category)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def update_stock_item(
    db: Session, item: StockItem, *, name: str, unit: str, price: float, category: str | None = None
) -> StockItem:
    item.name = name
    item.unit = unit
    item.price = price
    item.category = category
    db.commit()
    db.refresh(item)
    return item


def list_stock_items(db: Session) -> list[StockItem]:
    return list(db.scalars(select(StockItem).order_by(StockItem.name)))


def get_stock_item(db: Session, item_id: str) -> StockItem | None:
    return db.get(StockItem, item_id)


def stock_item_has_related_records(db: Session, item_id: str) -> bool:
    for model in (Sale, StockCount, StockDelivery):
        if db.scalar(select(model.id).where(model.item_id == item_id).limit(1)) is not None:
            return True
    return False


def delete_stock_item(db: Session, item: StockItem) -> bool:
    if stock_item_has_related_records(db, item.id):
        return False
    db.delete(item)
    db.commit()
    return True


def delete_all_stock_items(db: Session) -> int:
    for model in (Sale, StockCount, StockDelivery):
        db.execute(delete(model))
    result = db.execute(delete(StockItem))
    db.commit()
    return result.rowcount or 0
