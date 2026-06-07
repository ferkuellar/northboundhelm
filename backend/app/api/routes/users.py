from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.get("", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_session)) -> list[User]:
    result = await session.execute(select(User).order_by(User.created_at, User.email))
    return list(result.scalars().all())


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, session: AsyncSession = Depends(get_session)) -> User | JSONResponse:
    existing = await session.scalar(select(User).where(User.email == payload.email))
    if existing:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "code": "user_email_exists",
                "message": "A user with this email already exists.",
                "detail": {"email": str(payload.email)},
            },
        )

    user = User(**payload.model_dump())
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
