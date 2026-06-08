import uuid

from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.alert import BudgetAlertRead
from app.services.budget_service import budget_status


def _alert_message(project_name: str, period: str, level: str, consumed_pct) -> str:
    if level == "exceeded":
        return f"Project {project_name} has exceeded its {period} budget."
    return f"Project {project_name} has reached {consumed_pct}% of its {period} budget."


async def list_alerts(
    session: AsyncSession,
    project_id: uuid.UUID | None = None,
    period: str | None = None,
    level: str | None = None,
) -> list[BudgetAlertRead] | JSONResponse:
    statuses = await budget_status(session, project_id=project_id, period=period)
    if isinstance(statuses, JSONResponse):
        return statuses

    alerts: list[BudgetAlertRead] = []
    for item in statuses:
        if item.status == "ok":
            continue
        if level is not None and item.status != level:
            continue
        alerts.append(
            BudgetAlertRead(
                project_id=item.project_id,
                project_name=item.project_name,
                period=item.period,
                level=item.status,
                message=_alert_message(item.project_name, item.period, item.status, item.consumed_pct),
                budget_amount_usd=item.budget_amount_usd,
                spent_usd=item.spent_usd,
                consumed_pct=item.consumed_pct,
                alert_at_pct=item.alert_at_pct,
            )
        )

    return alerts
