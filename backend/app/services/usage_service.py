from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_request import AIRequest
from app.models.project import Project
from app.models.user import User
from app.schemas.usage import UsageByModel, UsageByProject, UsageByUser, UsageFilters


def _base_aggregates():
    return (
        func.count(AIRequest.id).label("request_count"),
        func.coalesce(func.sum(AIRequest.prompt_tokens), 0).label("prompt_tokens"),
        func.coalesce(func.sum(AIRequest.completion_tokens), 0).label("completion_tokens"),
        func.coalesce(func.sum(AIRequest.total_tokens), 0).label("total_tokens"),
        func.coalesce(func.sum(AIRequest.estimated_cost), 0).label("estimated_cost"),
    )


def _apply_filters(query, filters: UsageFilters):
    if filters.start_date is not None:
        query = query.where(AIRequest.created_at >= filters.start_date)
    if filters.end_date is not None:
        query = query.where(AIRequest.created_at <= filters.end_date)
    if filters.provider is not None:
        query = query.where(AIRequest.provider == filters.provider)
    if filters.model is not None:
        query = query.where(AIRequest.model == filters.model)
    if filters.status is not None:
        query = query.where(AIRequest.status == filters.status)
    if filters.project_id is not None:
        query = query.where(AIRequest.project_id == filters.project_id)
    if filters.user_id is not None:
        query = query.where(AIRequest.user_id == filters.user_id)
    return query


def _decimal(value) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


async def usage_by_project(session: AsyncSession, filters: UsageFilters) -> list[UsageByProject]:
    query = (
        select(Project.id, Project.name, *_base_aggregates())
        .join(AIRequest, AIRequest.project_id == Project.id)
        .group_by(Project.id, Project.name)
        .order_by(Project.name)
    )
    query = _apply_filters(query, filters)
    result = await session.execute(query)

    return [
        UsageByProject(
            project_id=row.id,
            project_name=row.name,
            request_count=row.request_count,
            prompt_tokens=row.prompt_tokens,
            completion_tokens=row.completion_tokens,
            total_tokens=row.total_tokens,
            estimated_cost=_decimal(row.estimated_cost),
        )
        for row in result.all()
    ]


async def usage_by_user(session: AsyncSession, filters: UsageFilters) -> list[UsageByUser]:
    query = (
        select(User.id, User.email, User.name, *_base_aggregates())
        .join(AIRequest, AIRequest.user_id == User.id)
        .group_by(User.id, User.email, User.name)
        .order_by(User.email)
    )
    query = _apply_filters(query, filters)
    result = await session.execute(query)

    return [
        UsageByUser(
            user_id=row.id,
            user_email=row.email,
            user_name=row.name,
            request_count=row.request_count,
            prompt_tokens=row.prompt_tokens,
            completion_tokens=row.completion_tokens,
            total_tokens=row.total_tokens,
            estimated_cost=_decimal(row.estimated_cost),
        )
        for row in result.all()
    ]


async def usage_by_model(session: AsyncSession, filters: UsageFilters) -> list[UsageByModel]:
    query = (
        select(AIRequest.provider, AIRequest.model, *_base_aggregates())
        .group_by(AIRequest.provider, AIRequest.model)
        .order_by(AIRequest.provider, AIRequest.model)
    )
    query = _apply_filters(query, filters)
    result = await session.execute(query)

    return [
        UsageByModel(
            provider=row.provider,
            model=row.model,
            request_count=row.request_count,
            prompt_tokens=row.prompt_tokens,
            completion_tokens=row.completion_tokens,
            total_tokens=row.total_tokens,
            estimated_cost=_decimal(row.estimated_cost),
        )
        for row in result.all()
    ]

