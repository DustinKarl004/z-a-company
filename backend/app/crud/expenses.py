import calendar
from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.branch import Branch
from app.models.expense import Expense
from app.models.sale import Sale
from app.models.stock_count import StockCount
from app.models.stock_delivery import StockDelivery


def create_expense(
    db: Session,
    *,
    branch_id: str,
    date_: date,
    description: str,
    amount: float | None,
    created_by_id: str,
) -> Expense:
    expense = Expense(
        branch_id=branch_id,
        date=date_,
        description=description,
        amount=amount,
        created_by_id=created_by_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def list_expenses(db: Session, *, branch_id: str | None = None, date_: date | None = None) -> list[Expense]:
    stmt = select(Expense)
    if branch_id:
        stmt = stmt.where(Expense.branch_id == branch_id)
    if date_:
        stmt = stmt.where(Expense.date == date_)
    return list(db.scalars(stmt.order_by(Expense.date.desc(), Expense.created_at.desc())))


def get_expense(db: Session, expense_id: str) -> Expense | None:
    return db.get(Expense, expense_id)


def get_expense_for_day(db: Session, *, branch_id: str, date_: date) -> Expense | None:
    return db.scalar(
        select(Expense).where(Expense.branch_id == branch_id, Expense.date == date_)
    )


def latest_expense_before(db: Session, *, branch_id: str, before_date: date) -> Expense | None:
    return db.scalar(
        select(Expense)
        .where(Expense.branch_id == branch_id, Expense.date < before_date)
        .order_by(Expense.date.desc())
        .limit(1)
    )


def carry_forward_expenses(db: Session, *, today: date, branch_id: str | None = None) -> set[str]:
    """Once a branch's daily bill has been entered, keep using that amount on
    later days until someone edits it, instead of starting each day blank.

    Only ever fills in `today` (never a future date) and never touches a day
    that already has its own entry, so past edits are untouched. Returns the
    set of branch ids that got a carried-forward row this call."""
    stmt = select(Branch.id)
    if branch_id:
        stmt = stmt.where(Branch.id == branch_id)
    carried = set()
    for (bid,) in db.execute(stmt).all():
        if get_expense_for_day(db, branch_id=bid, date_=today) is not None:
            continue
        latest = latest_expense_before(db, branch_id=bid, before_date=today)
        if latest is None:
            continue
        create_expense(
            db,
            branch_id=bid,
            date_=today,
            description=latest.description,
            amount=latest.amount,
            created_by_id=latest.created_by_id,
        )
        carried.add(bid)
    return carried


def project_future_expenses(
    db: Session, *, date_: date, branch_id: str | None = None, exclude_branch_ids: set[str]
) -> list[tuple[str, Expense]]:
    """Preview what a future day's bill would carry forward to, without
    actually saving anything until that day arrives.

    Returns (branch_id, source expense) pairs for branches that don't already
    have a real entry on `date_`, based on each branch's latest past entry."""
    stmt = select(Branch.id)
    if branch_id:
        stmt = stmt.where(Branch.id == branch_id)
    projected = []
    for (bid,) in db.execute(stmt).all():
        if bid in exclude_branch_ids:
            continue
        latest = latest_expense_before(db, branch_id=bid, before_date=date_)
        if latest is not None:
            projected.append((bid, latest))
    return projected


def update_expense(db: Session, expense: Expense, *, amount: float | None) -> Expense:
    expense.amount = amount
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense: Expense) -> None:
    db.delete(expense)
    db.commit()


def delete_month_data(db: Session, *, year: int, month: int) -> None:
    """Delete expenses, sales, stock counts, and stock deliveries for every branch
    in the given month (used to clear out old data once it's no longer needed).

    The closing stock count, sales, and daily bill on the last day of the month
    are kept — the stock count is the "opening" figure for the 1st day of the
    following month, and keeping that day's sales/bill alongside it means the
    last day still has a real, correct profit figure instead of one computed
    against a missing opening balance."""
    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    db.execute(delete(StockDelivery).where(StockDelivery.date >= start, StockDelivery.date <= end))
    for model in (Expense, Sale, StockCount):
        db.execute(delete(model).where(model.date >= start, model.date < end))
    db.commit()
