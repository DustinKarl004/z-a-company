from datetime import date as date_type, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.clock import local_today
from app.core.database import get_db
from app.core.deps import require_admin, require_admin_password
from app.core.scoping import resolve_branch_id
from app.crud.branches import get_branch
from app.crud.expenses import (
    carry_forward_expenses,
    create_expense,
    delete_expense,
    delete_month_data,
    get_expense,
    get_expense_for_day,
    list_expenses,
    project_future_expenses,
    update_expense,
)
from app.models.user import User
from app.schemas.expense import ExpenseCreate, ExpenseOut

router = APIRouter(prefix="/expenses", tags=["expenses"], dependencies=[Depends(require_admin)])


@router.post("", response_model=ExpenseOut, status_code=201)
def create_expense_endpoint(
    payload: ExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
) -> ExpenseOut:
    branch_id = resolve_branch_id(user, payload.branch_id)
    if get_branch(db, branch_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid branch_id")

    existing = get_expense_for_day(db, branch_id=branch_id, date_=payload.date)
    if existing is not None:
        expense = update_expense(db, existing, amount=payload.amount)
    else:
        expense = create_expense(
            db,
            branch_id=branch_id,
            date_=payload.date,
            description=payload.description,
            amount=payload.amount,
            created_by_id=user.id,
        )
    return ExpenseOut.model_validate(expense)


@router.get("", response_model=list[ExpenseOut])
def list_expenses_endpoint(
    branch_id: str | None = None,
    date: date_type | None = None,
    db: Session = Depends(get_db),
) -> list[ExpenseOut]:
    today = local_today()
    carried = set()
    if date is not None and date == today:
        carried = carry_forward_expenses(db, today=date, branch_id=branch_id)

    result = []
    for e in list_expenses(db, branch_id=branch_id, date_=date):
        out = ExpenseOut.model_validate(e)
        out.is_carried_forward = e.branch_id in carried
        result.append(out)

    if date is not None and date == today + timedelta(days=1):
        covered = {e.branch_id for e in result}
        for bid, latest in project_future_expenses(
            db, date_=date, branch_id=branch_id, exclude_branch_ids=covered
        ):
            result.append(
                ExpenseOut(
                    id=f"projected:{latest.id}",
                    branch_id=bid,
                    date=date,
                    description=latest.description,
                    amount=latest.amount,
                    created_by_id=latest.created_by_id,
                    created_at=latest.created_at,
                    is_projected=True,
                )
            )

    return result


@router.delete("/month", status_code=204)
def delete_month_data_endpoint(
    year: int,
    month: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_admin_password),
) -> None:
    if not 1 <= month <= 12:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid month")
    today = local_today()
    if (year, month) >= (today.year, today.month):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Can only delete data from a past month"
        )
    delete_month_data(db, year=year, month=month)


@router.delete("/{expense_id}", status_code=204)
def delete_expense_endpoint(expense_id: str, db: Session = Depends(get_db)) -> None:
    expense = get_expense(db, expense_id)
    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    delete_expense(db, expense)
