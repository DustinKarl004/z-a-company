from fastapi import APIRouter, Depends

from app.core.clock import local_today
from app.core.config import settings
from app.core.deps import require_staff_or_admin
from app.models.user import User
from app.schemas.clock import ClockOut

router = APIRouter(prefix="/clock", tags=["clock"])


@router.get("/today", response_model=ClockOut)
def get_today(user: User = Depends(require_staff_or_admin)) -> ClockOut:
    """The single source of truth for "today" — clients should use this instead
    of computing the business day from their own (possibly wrong) device clock.
    """
    return ClockOut(date=local_today(), cutoff_hour=settings.business_day_cutoff_hour)
