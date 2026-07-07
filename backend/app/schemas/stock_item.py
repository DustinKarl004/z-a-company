from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StockItemCreate(BaseModel):
    name: str
    unit: str
    price: float
    category: str | None = None


class StockItemUpdate(BaseModel):
    name: str
    unit: str
    price: float
    category: str | None = None


class StockItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    unit: str
    price: float
    category: str | None = None
    created_at: datetime
