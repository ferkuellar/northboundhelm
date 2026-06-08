import uuid
from decimal import Decimal

import pytest


async def create_user_and_project(client):
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": f"{uuid.uuid4()}@example.com",
            "name": "Budget User",
            "role": "developer",
        },
    )
    assert user_response.status_code == 201
    user = user_response.json()

    project_response = await client.post(
        "/api/v1/projects",
        json={
            "name": f"Budget Project {uuid.uuid4()}",
            "org_id": "default",
            "owner_id": user["id"],
            "budget_usd": "100.00",
        },
    )
    assert project_response.status_code == 201
    project = project_response.json()
    return user, project


async def create_ai_request(client, user_id: str, project_id: str, estimated_cost: str):
    response = await client.post(
        "/api/v1/ai/requests",
        json={
            "user_id": user_id,
            "project_id": project_id,
            "provider": "openai",
            "model": "gpt-4o",
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "estimated_cost": estimated_cost,
            "status": "success",
        },
    )
    assert response.status_code == 201
    return response.json()


def budget_payload(project_id: str, amount_usd: str = "10.00", alert_at_pct: int = 80) -> dict:
    return {
        "project_id": project_id,
        "period": "monthly",
        "amount_usd": amount_usd,
        "alert_at_pct": alert_at_pct,
    }


@pytest.mark.asyncio
async def test_list_budgets_empty_and_filter_by_project(client):
    empty_response = await client.get("/api/v1/budgets")
    assert empty_response.status_code == 200
    assert empty_response.json() == []

    _, project = await create_user_and_project(client)
    create_response = await client.post("/api/v1/budgets", json=budget_payload(project["id"]))
    assert create_response.status_code == 201

    filter_response = await client.get(f"/api/v1/budgets?project_id={project['id']}")
    assert filter_response.status_code == 200
    assert len(filter_response.json()) == 1
    assert filter_response.json()[0]["project_id"] == project["id"]


@pytest.mark.asyncio
async def test_invalid_budget_project_id_filter_returns_422(client):
    response = await client.get("/api/v1/budgets?project_id=not-a-uuid")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_and_update_budget(client):
    _, project = await create_user_and_project(client)

    create_response = await client.post("/api/v1/budgets", json=budget_payload(project["id"]))
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["project_id"] == project["id"]
    assert Decimal(created["amount_usd"]) == Decimal("10.00")

    update_payload = budget_payload(project["id"], amount_usd="25.00", alert_at_pct=75)
    update_response = await client.post("/api/v1/budgets", json=update_payload)
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["id"] == created["id"]
    assert Decimal(updated["amount_usd"]) == Decimal("25.00")
    assert Decimal(updated["alert_at_pct"]) == Decimal("75")

    list_response = await client.get(f"/api/v1/budgets?project_id={project['id']}&period=monthly")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1


@pytest.mark.asyncio
async def test_budget_create_validation_errors(client):
    missing_project_id = str(uuid.uuid4())

    unknown_response = await client.post("/api/v1/budgets", json=budget_payload(missing_project_id))
    assert unknown_response.status_code == 404
    assert unknown_response.json()["code"] == "project_not_found"

    _, project = await create_user_and_project(client)
    invalid_period = budget_payload(project["id"])
    invalid_period["period"] = "weekly"
    assert (await client.post("/api/v1/budgets", json=invalid_period)).status_code == 422

    invalid_amount = budget_payload(project["id"], amount_usd="0.00")
    assert (await client.post("/api/v1/budgets", json=invalid_amount)).status_code == 422

    invalid_threshold = budget_payload(project["id"], alert_at_pct=101)
    assert (await client.post("/api/v1/budgets", json=invalid_threshold)).status_code == 422


@pytest.mark.asyncio
async def test_budget_status_empty_and_no_usage_ok(client):
    empty_response = await client.get("/api/v1/budgets/status")
    assert empty_response.status_code == 200
    assert empty_response.json() == []

    _, project = await create_user_and_project(client)
    create_response = await client.post("/api/v1/budgets", json=budget_payload(project["id"]))
    assert create_response.status_code == 201

    status_response = await client.get(f"/api/v1/budgets/status?project_id={project['id']}")
    assert status_response.status_code == 200
    body = status_response.json()
    assert len(body) == 1
    assert body[0]["status"] == "ok"
    assert Decimal(body[0]["spent_usd"]) == Decimal("0.00")
    assert Decimal(body[0]["consumed_pct"]) == Decimal("0.00")


@pytest.mark.asyncio
async def test_budget_status_ok_warning_and_exceeded(client):
    user, ok_project = await create_user_and_project(client)
    _, warning_project = await create_user_and_project(client)
    _, exceeded_project = await create_user_and_project(client)

    for project in (ok_project, warning_project, exceeded_project):
        response = await client.post("/api/v1/budgets", json=budget_payload(project["id"]))
        assert response.status_code == 201

    await create_ai_request(client, user["id"], ok_project["id"], "1.00")
    await create_ai_request(client, user["id"], warning_project["id"], "8.00")
    await create_ai_request(client, user["id"], exceeded_project["id"], "10.00")

    response = await client.get("/api/v1/budgets/status")
    assert response.status_code == 200
    by_project = {item["project_id"]: item for item in response.json()}

    assert by_project[ok_project["id"]]["status"] == "ok"
    assert Decimal(by_project[ok_project["id"]]["spent_usd"]) == Decimal("1.00")
    assert Decimal(by_project[ok_project["id"]]["consumed_pct"]) == Decimal("10.00")

    assert by_project[warning_project["id"]]["status"] == "warning"
    assert Decimal(by_project[warning_project["id"]]["spent_usd"]) == Decimal("8.00")
    assert Decimal(by_project[warning_project["id"]]["consumed_pct"]) == Decimal("80.00")

    assert by_project[exceeded_project["id"]]["status"] == "exceeded"
    assert Decimal(by_project[exceeded_project["id"]]["spent_usd"]) == Decimal("10.00")
    assert Decimal(by_project[exceeded_project["id"]]["consumed_pct"]) == Decimal("100.00")


@pytest.mark.asyncio
async def test_budget_status_filter_and_invalid_filters(client):
    user, project = await create_user_and_project(client)
    await client.post("/api/v1/budgets", json=budget_payload(project["id"]))
    await create_ai_request(client, user["id"], project["id"], "3.00")

    filter_response = await client.get(f"/api/v1/budgets/status?project_id={project['id']}&period=monthly")
    assert filter_response.status_code == 200
    assert len(filter_response.json()) == 1
    assert filter_response.json()[0]["project_id"] == project["id"]

    invalid_uuid_response = await client.get("/api/v1/budgets/status?project_id=not-a-uuid")
    assert invalid_uuid_response.status_code == 422

    unknown_response = await client.get(f"/api/v1/budgets/status?project_id={uuid.uuid4()}")
    assert unknown_response.status_code == 404
    assert unknown_response.json()["code"] == "project_not_found"
