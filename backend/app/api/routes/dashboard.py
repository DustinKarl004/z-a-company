from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_admin
from app.crud.dashboard import monthly, overview
from app.schemas.dashboard import MonthlyResponse, OverviewResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"], dependencies=[Depends(require_admin)])


@router.get("/overview", response_model=OverviewResponse)
def overview_endpoint(
    date: date | None = Query(None), db: Session = Depends(get_db)
) -> OverviewResponse:
    return OverviewResponse.model_validate(overview(db, date))


@router.get("/monthly", response_model=MonthlyResponse)
def monthly_endpoint(
    year: int = Query(...), month: int = Query(..., ge=1, le=12), db: Session = Depends(get_db)
) -> MonthlyResponse:
    return MonthlyResponse.model_validate(monthly(db, year, month))
