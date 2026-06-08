import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


AlertLevel = Literal["warning", "exceeded"]


class BudgetAlertRead(BaseModel):
    project_id: uuid.UUID
    project_name: str
    period: str
    level: AlertLevel
    message: str
    budget_amount_usd: Decimal
    spent_usd: Decimal
    consumed_pct: Decimal
    alert_at_pct: Decimal
