import uuid
from decimal import Decimal

import pytest


async def create_user_and_project(client, name_prefix: str = "Alert Project"):
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": f"{uuid.uuid4()}@example.com",
            "name": "Alert User",
            "role": "developer",
        },
    )
    assert user_response.status_code == 201
    user = user_response.json()

    project_response = await client.post(
        "/api/v1/projects",
        json={
            "name": f"{name_prefix} {uuid.uuid4()}",
            "org_id": "default",
            "owner_id": user["id"],
            "budget_usd": "100.00",
        },
    )
    assert project_response.status_code == 201
    project = project_response.json()
    return user, project


async def create_budget(client, project_id: str, period: str = "monthly", amount: str = "10.00", threshold: int = 80):
    response = await client.post(
        "/api/v1/budgets",
        json={
            "project_id": project_id,
            "period": period,
            "amount_usd": amount,
            "alert_at_pct": threshold,
        },
    )
    assert response.status_code in (200, 201)
    return response.json()


async def create_ai_request(client, user_id: str, project_id: str, cost: str):
    response = await client.post(
        "/api/v1/ai/requests",
        json={
            "user_id": user_id,
            "project_id": project_id,
            "provider": "openai",
            "model": "gpt-4o",
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "estimated_cost": cost,
            "status": "success",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_alerts_empty_and_ok_budget_excluded(client):
    empty_response = await client.get("/api/v1/alerts")
    assert empty_response.status_code == 200
    assert empty_response.json() == []

    user, project = await create_user_and_project(client)
    await create_budget(client, project["id"])
    await create_ai_request(client, user["id"], project["id"], "1.00")

    ok_response = await client.get("/api/v1/alerts")
    assert ok_response.status_code == 200
    assert ok_response.json() == []


@pytest.mark.asyncio
async def test_warning_alert_at_threshold(client):
    user, project = await create_user_and_project(client)
    await create_budget(client, project["id"])
    await create_ai_request(client, user["id"], project["id"], "8.00")

    response = await client.get("/api/v1/alerts")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    alert = body[0]
    assert alert["project_id"] == project["id"]
    assert alert["project_name"] == project["name"]
    assert alert["period"] == "monthly"
    assert alert["level"] == "warning"
    assert "reached 80.00%" in alert["message"]
    assert Decimal(alert["budget_amount_usd"]) == Decimal("10.00")
    assert Decimal(alert["spent_usd"]) == Decimal("8.00")
    assert Decimal(alert["consumed_pct"]) == Decimal("80.00")
    assert Decimal(alert["alert_at_pct"]) == Decimal("80.00")


@pytest.mark.asyncio
async def test_warning_alert_above_threshold_below_budget(client):
    user, project = await create_user_and_project(client)
    await create_budget(client, project["id"])
    await create_ai_request(client, user["id"], project["id"], "9.00")

    response = await client.get("/api/v1/alerts")

    assert response.status_code == 200
    alert = response.json()[0]
    assert alert["level"] == "warning"
    assert Decimal(alert["spent_usd"]) == Decimal("9.00")
    assert Decimal(alert["consumed_pct"]) == Decimal("90.00")


@pytest.mark.asyncio
async def test_exceeded_alert_at_and_above_budget(client):
    user, at_budget_project = await create_user_and_project(client, "At Budget")
    _, above_budget_project = await create_user_and_project(client, "Above Budget")
    await create_budget(client, at_budget_project["id"])
    await create_budget(client, above_budget_project["id"])
    await create_ai_request(client, user["id"], at_budget_project["id"], "10.00")
    await create_ai_request(client, user["id"], above_budget_project["id"], "12.50")

    response = await client.get("/api/v1/alerts")

    assert response.status_code == 200
    by_project = {item["project_id"]: item for item in response.json()}
    assert by_project[at_budget_project["id"]]["level"] == "exceeded"
    assert "exceeded its monthly budget" in by_project[at_budget_project["id"]]["message"]
    assert Decimal(by_project[at_budget_project["id"]]["consumed_pct"]) == Decimal("100.00")
    assert by_project[above_budget_project["id"]]["level"] == "exceeded"
    assert Decimal(by_project[above_budget_project["id"]]["consumed_pct"]) == Decimal("125.00")


@pytest.mark.asyncio
async def test_alert_filters_by_project_period_and_level(client):
    user, warning_project = await create_user_and_project(client, "Warning")
    _, exceeded_project = await create_user_and_project(client, "Exceeded")
    await create_budget(client, warning_project["id"], period="monthly")
    await create_budget(client, exceeded_project["id"], period="yearly")
    await create_ai_request(client, user["id"], warning_project["id"], "8.00")
    await create_ai_request(client, user["id"], exceeded_project["id"], "10.00")

    project_response = await client.get(f"/api/v1/alerts?project_id={warning_project['id']}")
    assert project_response.status_code == 200
    assert len(project_response.json()) == 1
    assert project_response.json()[0]["project_id"] == warning_project["id"]

    period_response = await client.get("/api/v1/alerts?period=yearly")
    assert period_response.status_code == 200
    assert len(period_response.json()) == 1
    assert period_response.json()[0]["period"] == "yearly"

    warning_response = await client.get("/api/v1/alerts?level=warning")
    assert warning_response.status_code == 200
    assert {item["level"] for item in warning_response.json()} == {"warning"}

    exceeded_response = await client.get("/api/v1/alerts?level=exceeded")
    assert exceeded_response.status_code == 200
    assert {item["level"] for item in exceeded_response.json()} == {"exceeded"}


@pytest.mark.asyncio
async def test_alert_filter_validation_errors(client):
    invalid_uuid_response = await client.get("/api/v1/alerts?project_id=not-a-uuid")
    assert invalid_uuid_response.status_code == 422

    unknown_response = await client.get(f"/api/v1/alerts?project_id={uuid.uuid4()}")
    assert unknown_response.status_code == 404
    assert unknown_response.json()["code"] == "project_not_found"

    invalid_period_response = await client.get("/api/v1/alerts?period=weekly")
    assert invalid_period_response.status_code == 422

    invalid_level_response = await client.get("/api/v1/alerts?level=ok")
    assert invalid_level_response.status_code == 422
