import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    name: str
    org_id: str = "default"
    owner_id: uuid.UUID | None = None
    budget_usd: Decimal = Decimal("0.00")
    description: str | None = None
    is_active: bool = True


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    org_id: str
    owner_id: uuid.UUID | None
    budget_usd: Decimal
    description: str | None
    is_active: bool
    created_at: datetime

