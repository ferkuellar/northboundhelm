import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_request import AIRequest
from app.models.project import Project
from app.models.user import User
from app.schemas.ai_request import AIRequestCreate


async def user_exists(session: AsyncSession, user_id: uuid.UUID) -> bool:
    return await session.scalar(select(User.id).where(User.id == user_id)) is not None


async def project_exists(session: AsyncSession, project_id: uuid.UUID) -> bool:
    return await session.scalar(select(Project.id).where(Project.id == project_id)) is not None


async def record_ai_request(session: AsyncSession, payload: AIRequestCreate) -> AIRequest:
    ai_request = AIRequest(
        user_id=payload.user_id,
        project_id=payload.project_id,
        provider=payload.provider,
        model=payload.model,
        prompt_tokens=payload.prompt_tokens,
        completion_tokens=payload.completion_tokens,
        total_tokens=payload.prompt_tokens + payload.completion_tokens,
        estimated_cost=payload.estimated_cost,
        latency_ms=payload.latency_ms,
        status=payload.status,
        request_metadata=payload.metadata,
    )
    session.add(ai_request)
    await session.commit()
    await session.refresh(ai_request)
    return ai_request

