import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.alert import AlertLevel, BudgetAlertRead
from app.schemas.budget import BudgetPeriod
from app.services.alert_service import list_alerts

router = APIRouter()


@router.get("", response_model=list[BudgetAlertRead])
async def get_alerts(
    project_id: uuid.UUID | None = Query(default=None),
    period: BudgetPeriod | None = Query(default=None),
    level: AlertLevel | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    return await list_alerts(session, project_id=project_id, period=period, level=level)
