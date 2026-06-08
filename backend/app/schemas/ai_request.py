import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator


class AIRequestCreate(BaseModel):
    user_id: uuid.UUID
    project_id: uuid.UUID
    provider: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=150)
    prompt_tokens: int = Field(ge=0)
    completion_tokens: int = Field(ge=0)
    total_tokens: int | None = Field(default=None, ge=0)
    estimated_cost: Decimal = Field(default=Decimal("0.000000"), ge=Decimal("0.000000"))
    latency_ms: int | None = Field(default=None, ge=0)
    status: str = Field(min_length=1, max_length=50)
    metadata: dict[str, Any] | None = None

    @model_validator(mode="after")
    def calculate_total_tokens(self) -> "AIRequestCreate":
        expected_total = self.prompt_tokens + self.completion_tokens
        if self.total_tokens != expected_total:
            self.total_tokens = expected_total
        return self


class AIRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    user_id: uuid.UUID
    project_id: uuid.UUID
    provider: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost: Decimal
    latency_ms: int | None
    status: str
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias=AliasChoices("request_metadata", "metadata"),
        serialization_alias="metadata",
    )
    created_at: datetime
