import uuid

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.ai_request import AIRequest
from app.schemas.ai_request import AIRequestCreate, AIRequestRead
from app.services.metering_service import project_exists, record_ai_request, user_exists

router = APIRouter()


@router.post("/requests", response_model=AIRequestRead, status_code=status.HTTP_201_CREATED)
async def create_ai_request(
    payload: AIRequestCreate,
    session: AsyncSession = Depends(get_session),
) -> AIRequest | JSONResponse:
    if not await user_exists(session, payload.user_id):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "code": "user_not_found",
                "message": "User not found.",
                "detail": {"user_id": str(payload.user_id)},
            },
        )

    if not await project_exists(session, payload.project_id):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "code": "project_not_found",
                "message": "Project not found.",
                "detail": {"project_id": str(payload.project_id)},
            },
        )

    return await record_ai_request(session, payload)


@router.get("/requests", response_model=list[AIRequestRead])
async def list_ai_requests(
    user_id: uuid.UUID | None = Query(default=None),
    project_id: uuid.UUID | None = Query(default=None),
    provider: str | None = Query(default=None),
    model: str | None = Query(default=None),
    status_value: str | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_session),
) -> list[AIRequest]:
    query = select(AIRequest)
    if user_id is not None:
        query = query.where(AIRequest.user_id == user_id)
    if project_id is not None:
        query = query.where(AIRequest.project_id == project_id)
    if provider is not None:
        query = query.where(AIRequest.provider == provider)
    if model is not None:
        query = query.where(AIRequest.model == model)
    if status_value is not None:
        query = query.where(AIRequest.status == status_value)

    result = await session.execute(query.order_by(AIRequest.created_at.desc()))
    return list(result.scalars().all())


@router.get("/requests/{request_id}", response_model=AIRequestRead)
async def get_ai_request(
    request_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> AIRequest | JSONResponse:
    ai_request = await session.get(AIRequest, request_id)
    if ai_request is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "code": "ai_request_not_found",
                "message": "AI request not found.",
                "detail": {"request_id": str(request_id)},
            },
        )

    return ai_request

