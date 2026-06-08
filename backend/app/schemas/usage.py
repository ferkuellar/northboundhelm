import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class UsageFilters(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    provider: str | None = None
    model: str | None = None
    status: str | None = None
    project_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None


class UsageByProject(BaseModel):
    project_id: uuid.UUID
    project_name: str
    request_count: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: Decimal


class UsageByUser(BaseModel):
    user_id: uuid.UUID
    user_email: str
    user_name: str
    request_count: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: Decimal


class UsageByModel(BaseModel):
    provider: str
    model: str
    request_count: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: Decimal

