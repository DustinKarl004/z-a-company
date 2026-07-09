from datetime import date as date_type

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_staff_or_admin
from app.core.scoping import ensure_creatable_date, ensure_editable, resolve_branch_id
from app.crud.branches import get_branch
from app.crud.stock_items import get_stock_item
from app.crud.stock_needs import (
    create_need,
    delete_need,
    get_need,
    get_need_for_day,
    list_needs,
    update_need,
)
from app.models.user import User
from app.schemas.stock_need import StockNeedCreate, StockNeedOut, StockNeedUpdate

router = APIRouter(prefix="/stock-needs", tags=["stock-needs"])


@router.post("", response_model=StockNeedOut, status_code=201)
def create_need_endpoint(
    payload: StockNeedCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff_or_admin),
) -> StockNeedOut:
    branch_id = resolve_branch_id(user, payload.branch_id)
    if get_branch(db, branch_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid branch_id")
    if get_stock_item(db, payload.item_id) is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid item_id")
    ensure_creatable_date(user, payload.date)

    existing = get_need_for_day(db, branch_id=branch_id, item_id=payload.item_id, date_=payload.date)
    if existing is not None:
        return StockNeedOut.model_validate(existing)

    need = create_need(
        db,
        branch_id=branch_id,
        item_id=payload.item_id,
        date_=payload.date,
        created_by_id=user.id,
    )
    return StockNeedOut.model_validate(need)


@router.get("", response_model=list[StockNeedOut])
def list_needs_endpoint(
    branch_id: str | None = None,
    date: date_type | None = None,
    is_delivered: bool | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff_or_admin),
) -> list[StockNeedOut]:
    effective_branch_id = branch_id if (user.role == "admin" or not user.branch_id) else user.branch_id
    return [
        StockNeedOut.model_validate(n)
        for n in list_needs(db, branch_id=effective_branch_id, date_=date, is_delivered=is_delivered)
    ]


@router.patch("/{need_id}", response_model=StockNeedOut)
def update_need_endpoint(
    need_id: str,
    payload: StockNeedUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff_or_admin),
) -> StockNeedOut:
    need = get_need(db, need_id)
    if need is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Need not found")
    if user.role == "staff" and user.branch_id and need.branch_id != user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your branch")

    if payload.is_delivered is None:
        return StockNeedOut.model_validate(need)
    # Marking delivered isn't date-restricted — delivery staff routinely clear needs
    # from prior days.
    updated = update_need(db, need, is_delivered=payload.is_delivered)
    return StockNeedOut.model_validate(updated)


@router.delete("/{need_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_need_endpoint(
    need_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff_or_admin),
) -> None:
    need = get_need(db, need_id)
    if need is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Need not found")
    if user.role == "staff" and user.branch_id and need.branch_id != user.branch_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your branch")
    ensure_editable(user, need.date)
    delete_need(db, need)
