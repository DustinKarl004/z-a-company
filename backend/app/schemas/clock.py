from datetime import date as date_type

from pydantic import BaseModel


class ClockOut(BaseModel):
    date: date_type
    cutoff_hour: int
