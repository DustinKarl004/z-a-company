from datetime import date as date_type, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.clock import local_today


class StockNeedCreate(BaseModel):
    branch_id: str | None = None
    item_id: str
    date: date_type = Field(default_factory=local_today)


class StockNeedUpdate(BaseModel):
    is_delivered: bool | None = None


class StockNeedOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    branch_id: str
    item_id: str
    date: date_type
    is_delivered: bool
    created_by_id: str
    created_at: datetime
