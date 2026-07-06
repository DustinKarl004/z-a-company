from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.branch import Branch
from app.models.sale import Sale
from app.models.stock_count import StockCount
from app.models.stock_delivery import StockDelivery
from app.models.user import User


def create_branch(db: Session, *, name: str) -> Branch:
    branch = Branch(name=name)
    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


def list_branches(db: Session) -> list[Branch]:
    return list(db.scalars(select(Branch).order_by(Branch.name)))


def get_branch(db: Session, branch_id: str) -> Branch | None:
    return db.get(Branch, branch_id)


def update_branch(db: Session, branch: Branch, *, name: str) -> Branch:
    branch.name = name
    db.commit()
    db.refresh(branch)
    return branch


def branch_has_related_records(db: Session, branch_id: str) -> bool:
    for model in (User, Sale, StockCount, StockDelivery):
        if db.scalar(select(model.id).where(model.branch_id == branch_id).limit(1)) is not None:
            return True
    return False


def delete_branch(db: Session, branch: Branch) -> bool:
    if branch_has_related_records(db, branch.id):
        return False
    db.delete(branch)
    db.commit()
    return True
