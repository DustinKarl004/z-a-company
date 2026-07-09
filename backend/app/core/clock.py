from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.config import settings


def local_today() -> date:
    """Current business day in the configured timezone, not the server host's.

    Branches can stay open past midnight, so before `business_day_cutoff_hour`
    the business day hasn't rolled over yet — it's still "yesterday".
    """
    now = datetime.now(ZoneInfo(settings.app_timezone))
    if now.hour < settings.business_day_cutoff_hour:
        return (now - timedelta(days=1)).date()
    return now.date()
