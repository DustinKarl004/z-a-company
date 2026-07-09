from datetime import date as date_type

from sqlalchemy import Boolean, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdMixin


class StockNeed(Base, IdMixin):
    __tablename__ = "stock_needs"

    branch_id: Mapped[str] = mapped_column(String(12), ForeignKey("branches.id"), nullable=False)
    item_id: Mapped[str] = mapped_column(String(12), ForeignKey("stock_items.id"), nullable=False)
    date: Mapped[date_type] = mapped_column(Date, nullable=False)
    is_delivered: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by_id: Mapped[str] = mapped_column(String(12), ForeignKey("users.id"), nullable=False)
