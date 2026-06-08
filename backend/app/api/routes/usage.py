import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.usage import UsageByModel, UsageByProject, UsageByUser, UsageFilters
from app.services.usage_service import usage_by_model, usage_by_project, usage_by_user

router = APIRouter()


def usage_filters(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    provider: str | None = Query(default=None),
    model: str | None = Query(default=None),
    status: str | None = Query(default=None),
    project_id: uuid.UUID | None = Query(default=None),
    user_id: uuid.UUID | None = Query(default=None),
) -> UsageFilters:
    return UsageFilters(
        start_date=start_date,
        end_date=end_date,
        provider=provider,
        model=model,
        status=status,
        project_id=project_id,
        user_id=user_id,
    )


@router.get("/by-project", response_model=list[UsageByProject])
async def get_usage_by_project(
    filters: UsageFilters = Depends(usage_filters),
    session: AsyncSession = Depends(get_session),
) -> list[UsageByProject]:
    return await usage_by_project(session, filters)


@router.get("/by-user", response_model=list[UsageByUser])
async def get_usage_by_user(
    filters: UsageFilters = Depends(usage_filters),
    session: AsyncSession = Depends(get_session),
) -> list[UsageByUser]:
    return await usage_by_user(session, filters)


@router.get("/by-model", response_model=list[UsageByModel])
async def get_usage_by_model(
    filters: UsageFilters = Depends(usage_filters),
    session: AsyncSession = Depends(get_session),
) -> list[UsageByModel]:
    return await usage_by_model(session, filters)

