from decimal import Decimal

import pytest


async def create_user(client, email: str, name: str):
    response = await client.post(
        "/api/v1/users",
        json={
            "email": email,
            "name": name,
            "role": "developer",
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_project(client, name: str, owner_id: str):
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": name,
            "org_id": "default",
            "owner_id": owner_id,
            "budget_usd": "1000.00",
        },
    )
    assert response.status_code == 201
    return response.json()


async def create_ai_request(
    client,
    *,
    user_id: str,
    project_id: str,
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    estimated_cost: str,
    status: str = "success",
):
    response = await client.post(
        "/api/v1/ai/requests",
        json={
            "user_id": user_id,
            "project_id": project_id,
            "provider": provider,
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "estimated_cost": estimated_cost,
            "status": status,
        },
    )
    assert response.status_code == 201
    return response.json()


async def seed_usage_data(client):
    user_one = await create_user(client, "usage-one@example.com", "Usage One")
    user_two = await create_user(client, "usage-two@example.com", "Usage Two")
    project_one = await create_project(client, "Usage Project One", user_one["id"])
    project_two = await create_project(client, "Usage Project Two", user_two["id"])

    await create_ai_request(
        client,
        user_id=user_one["id"],
        project_id=project_one["id"],
        provider="openai",
        model="gpt-4o",
        prompt_tokens=100,
        completion_tokens=50,
        estimated_cost="0.001000",
    )
    await create_ai_request(
        client,
        user_id=user_one["id"],
        project_id=project_one["id"],
        provider="openai",
        model="gpt-4o",
        prompt_tokens=200,
        completion_tokens=100,
        estimated_cost="0.002000",
    )
    await create_ai_request(
        client,
        user_id=user_two["id"],
        project_id=project_two["id"],
        provider="anthropic",
        model="claude-3-5-sonnet",
        prompt_tokens=400,
        completion_tokens=100,
        estimated_cost="0.004000",
        status="error",
    )

    return user_one, user_two, project_one, project_two


def decimal_value(value) -> Decimal:
    return Decimal(str(value))


@pytest.mark.asyncio
async def test_usage_by_project_aggregates_correctly(client):
    _, _, project_one, _ = await seed_usage_data(client)

    response = await client.get("/api/v1/usage/by-project")

    assert response.status_code == 200
    rows = response.json()
    project_row = next(row for row in rows if row["project_id"] == project_one["id"])
    assert project_row["project_name"] == "Usage Project One"
    assert project_row["request_count"] == 2
    assert project_row["prompt_tokens"] == 300
    assert project_row["completion_tokens"] == 150
    assert project_row["total_tokens"] == 450
    assert decimal_value(project_row["estimated_cost"]) == Decimal("0.003000")


@pytest.mark.asyncio
async def test_usage_by_user_aggregates_correctly(client):
    user_one, _, _, _ = await seed_usage_data(client)

    response = await client.get("/api/v1/usage/by-user")

    assert response.status_code == 200
    rows = response.json()
    user_row = next(row for row in rows if row["user_id"] == user_one["id"])
    assert user_row["user_email"] == "usage-one@example.com"
    assert user_row["user_name"] == "Usage One"
    assert user_row["request_count"] == 2
    assert user_row["prompt_tokens"] == 300
    assert user_row["completion_tokens"] == 150
    assert user_row["total_tokens"] == 450
    assert decimal_value(user_row["estimated_cost"]) == Decimal("0.003000")


@pytest.mark.asyncio
async def test_usage_by_model_aggregates_correctly(client):
    await seed_usage_data(client)

    response = await client.get("/api/v1/usage/by-model")

    assert response.status_code == 200
    rows = response.json()
    model_row = next(row for row in rows if row["provider"] == "openai" and row["model"] == "gpt-4o")
    assert model_row["request_count"] == 2
    assert model_row["prompt_tokens"] == 300
    assert model_row["completion_tokens"] == 150
    assert model_row["total_tokens"] == 450
    assert decimal_value(model_row["estimated_cost"]) == Decimal("0.003000")


@pytest.mark.asyncio
async def test_usage_filters_return_expected_rows(client):
    user_one, user_two, project_one, project_two = await seed_usage_data(client)

    provider_response = await client.get("/api/v1/usage/by-model?provider=openai")
    assert provider_response.status_code == 200
    assert len(provider_response.json()) == 1
    assert provider_response.json()[0]["provider"] == "openai"

    model_response = await client.get("/api/v1/usage/by-model?model=claude-3-5-sonnet")
    assert model_response.status_code == 200
    assert len(model_response.json()) == 1
    assert model_response.json()[0]["model"] == "claude-3-5-sonnet"

    status_response = await client.get("/api/v1/usage/by-user?status=error")
    assert status_response.status_code == 200
    assert status_response.json()[0]["user_id"] == user_two["id"]

    project_response = await client.get(f"/api/v1/usage/by-project?project_id={project_one['id']}")
    assert project_response.status_code == 200
    assert len(project_response.json()) == 1
    assert project_response.json()[0]["project_id"] == project_one["id"]

    user_response = await client.get(f"/api/v1/usage/by-project?user_id={user_one['id']}")
    assert user_response.status_code == 200
    assert len(user_response.json()) == 1
    assert user_response.json()[0]["project_id"] == project_one["id"]

    other_project_response = await client.get(f"/api/v1/usage/by-user?project_id={project_two['id']}")
    assert other_project_response.status_code == 200
    assert other_project_response.json()[0]["user_id"] == user_two["id"]


@pytest.mark.asyncio
async def test_usage_empty_filter_result_returns_empty_list(client):
    await seed_usage_data(client)

    response = await client.get("/api/v1/usage/by-project?provider=none")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_usage_date_filters(client):
    await seed_usage_data(client)

    future_response = await client.get("/api/v1/usage/by-model?start_date=2100-01-01T00:00:00Z")
    assert future_response.status_code == 200
    assert future_response.json() == []

    current_range_response = await client.get(
        "/api/v1/usage/by-model?start_date=2000-01-01T00:00:00Z&end_date=2100-01-01T00:00:00Z"
    )
    assert current_range_response.status_code == 200
    assert len(current_range_response.json()) == 2


@pytest.mark.asyncio
async def test_usage_invalid_uuid_filter_returns_422(client):
    response = await client.get("/api/v1/usage/by-project?project_id=not-a-uuid")

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_usage_invalid_datetime_filter_returns_422(client):
    response = await client.get("/api/v1/usage/by-model?start_date=not-a-date")

    assert response.status_code == 422

