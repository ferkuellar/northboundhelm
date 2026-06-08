import uuid
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from fastapi import status
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_request import AIRequest
from app.models.budget import Budget
from app.models.project import Project
from app.schemas.budget import BudgetCreate, BudgetStatusRead


def project_not_found_response(project_id: uuid.UUID) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "code": "project_not_found",
            "message": "Project not found.",
            "detail": {"project_id": str(project_id)},
        },
    )


def _money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _decimal(value) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def _period_start(period: str) -> datetime:
    now = datetime.now(timezone.utc)
    if period == "monthly":
        return datetime(now.year, now.month, 1, tzinfo=timezone.utc)
    return datetime(now.year, 1, 1, tzinfo=timezone.utc)


async def list_budgets(
    session: AsyncSession,
    project_id: uuid.UUID | None = None,
    period: str | None = None,
) -> list[Budget]:
    query = select(Budget).order_by(Budget.created_at, Budget.period)
    if project_id is not None:
        query = query.where(Budget.project_id == project_id)
    if period is not None:
        query = query.where(Budget.period == period)
    result = await session.execute(query)
    return list(result.scalars().all())


async def create_or_update_budget(
    session: AsyncSession,
    payload: BudgetCreate,
) -> tuple[Budget | JSONResponse, int]:
    project = await session.get(Project, payload.project_id)
    if project is None:
        return project_not_found_response(payload.project_id), status.HTTP_404_NOT_FOUND

    budget = await session.scalar(
        select(Budget).where(Budget.project_id == payload.project_id, Budget.period == payload.period)
    )
    response_status = status.HTTP_200_OK

    if budget is None:
        budget = Budget(project_id=payload.project_id, period=payload.period)
        session.add(budget)
        response_status = status.HTTP_201_CREATED

    budget.amount_usd = payload.amount_usd
    budget.alert_at_pct = Decimal(payload.alert_at_pct)
    await session.commit()
    await session.refresh(budget)
    return budget, response_status


async def budget_status(
    session: AsyncSession,
    project_id: uuid.UUID | None = None,
    period: str | None = None,
) -> list[BudgetStatusRead] | JSONResponse:
    if project_id is not None and await session.get(Project, project_id) is None:
        return project_not_found_response(project_id)

    query = (
        select(Budget, Project.name)
        .join(Project, Project.id == Budget.project_id)
        .order_by(Project.name, Budget.period)
    )
    if project_id is not None:
        query = query.where(Budget.project_id == project_id)
    if period is not None:
        query = query.where(Budget.period == period)

    result = await session.execute(query)
    rows = result.all()
    statuses: list[BudgetStatusRead] = []

    for budget, project_name in rows:
        spent_result = await session.execute(
            select(func.coalesce(func.sum(AIRequest.estimated_cost), 0)).where(
                AIRequest.project_id == budget.project_id,
                AIRequest.created_at >= _period_start(budget.period),
            )
        )
        spent = _money(_decimal(spent_result.scalar_one()))
        amount = _money(_decimal(budget.amount_usd))
        consumed_pct = _money((spent / amount) * Decimal("100"))
        alert_at_pct = _decimal(budget.alert_at_pct)

        if spent >= amount:
            status_value = "exceeded"
        elif consumed_pct >= alert_at_pct:
            status_value = "warning"
        else:
            status_value = "ok"

        statuses.append(
            BudgetStatusRead(
                project_id=budget.project_id,
                project_name=project_name,
                period=budget.period,
                budget_amount_usd=amount,
                spent_usd=spent,
                consumed_pct=consumed_pct,
                alert_at_pct=alert_at_pct,
                status=status_value,
            )
        )

    return statuses
