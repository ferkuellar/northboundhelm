import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


BudgetPeriod = Literal["monthly", "yearly"]
BudgetStatusValue = Literal["ok", "warning", "exceeded"]


class BudgetCreate(BaseModel):
    project_id: uuid.UUID
    period: BudgetPeriod
    amount_usd: Decimal = Field(gt=Decimal("0.00"))
    alert_at_pct: int = Field(ge=1, le=100)


class BudgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    period: str
    amount_usd: Decimal
    alert_at_pct: Decimal
    created_at: datetime


class BudgetStatusRead(BaseModel):
    project_id: uuid.UUID
    project_name: str
    period: str
    budget_amount_usd: Decimal
    spent_usd: Decimal
    consumed_pct: Decimal
    alert_at_pct: Decimal
    status: BudgetStatusValue
