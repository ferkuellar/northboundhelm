import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=255)
    role: str = Field(default="developer", min_length=1, max_length=50)
    org_id: str = Field(default="default", min_length=1, max_length=100)
    is_active: bool = True


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    name: str
    role: str
    org_id: str
    is_active: bool
    created_at: datetime
