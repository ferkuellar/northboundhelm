import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    org_id: str = Field(default="default", min_length=1, max_length=100)
    owner_id: uuid.UUID | None = None
    budget_usd: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0.00"))
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
