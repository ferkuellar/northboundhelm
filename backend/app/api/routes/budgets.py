import uuid

from fastapi import APIRouter, Depends, Query, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.budget import BudgetCreate, BudgetPeriod, BudgetRead, BudgetStatusRead
from app.services.budget_service import budget_status, create_or_update_budget, list_budgets

router = APIRouter()


@router.get("", response_model=list[BudgetRead])
async def get_budgets(
    project_id: uuid.UUID | None = Query(default=None),
    period: BudgetPeriod | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list:
    return await list_budgets(session, project_id=project_id, period=period)


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
async def post_budget(
    payload: BudgetCreate,
    response: Response,
    session: AsyncSession = Depends(get_session),
):
    budget, response_status = await create_or_update_budget(session, payload)
    if isinstance(budget, JSONResponse):
        return budget
    response.status_code = response_status
    return budget


@router.get("/status", response_model=list[BudgetStatusRead])
async def get_budget_status(
    project_id: uuid.UUID | None = Query(default=None),
    period: BudgetPeriod | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    return await budget_status(session, project_id=project_id, period=period)
