import uuid

import pytest


async def create_user_and_project(client):
    user_response = await client.post(
        "/api/v1/users",
        json={
            "email": f"{uuid.uuid4()}@example.com",
            "name": "Metering User",
            "role": "developer",
        },
    )
    assert user_response.status_code == 201
    user = user_response.json()

    project_response = await client.post(
        "/api/v1/projects",
        json={
            "name": f"Metering Project {uuid.uuid4()}",
            "org_id": "default",
            "owner_id": user["id"],
            "budget_usd": "100.00",
        },
    )
    assert project_response.status_code == 201
    project = project_response.json()
    return user, project


def metering_payload(user_id: str, project_id: str) -> dict:
    return {
        "user_id": user_id,
        "project_id": project_id,
        "provider": "openai",
        "model": "gpt-4o",
        "prompt_tokens": 1000,
        "completion_tokens": 500,
        "total_tokens": 1,
        "estimated_cost": "0.005000",
        "latency_ms": 1200,
        "status": "success",
        "metadata": {
            "environment": "test",
            "source": "pytest",
        },
    }


@pytest.mark.asyncio
async def test_create_list_and_get_ai_request(client):
    user, project = await create_user_and_project(client)

    create_response = await client.post(
        "/api/v1/ai/requests",
        json=metering_payload(user["id"], project["id"]),
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["user_id"] == user["id"]
    assert created["project_id"] == project["id"]
    assert created["provider"] == "openai"
    assert created["model"] == "gpt-4o"
    assert created["prompt_tokens"] == 1000
    assert created["completion_tokens"] == 500
    assert created["total_tokens"] == 1500
    assert created["metadata"] == {"environment": "test", "source": "pytest"}

    list_response = await client.get("/api/v1/ai/requests")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]

    detail_response = await client.get(f"/api/v1/ai/requests/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]


@pytest.mark.asyncio
async def test_unknown_ai_request_returns_404(client):
    missing_id = str(uuid.uuid4())

    response = await client.get(f"/api/v1/ai/requests/{missing_id}")

    assert response.status_code == 404
    assert response.json() == {
        "code": "ai_request_not_found",
        "message": "AI request not found.",
        "detail": {"request_id": missing_id},
    }


@pytest.mark.asyncio
async def test_unknown_user_returns_404(client):
    _, project = await create_user_and_project(client)
    missing_user_id = str(uuid.uuid4())

    response = await client.post(
        "/api/v1/ai/requests",
        json=metering_payload(missing_user_id, project["id"]),
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "user_not_found",
        "message": "User not found.",
        "detail": {"user_id": missing_user_id},
    }


@pytest.mark.asyncio
async def test_unknown_project_returns_404(client):
    user, _ = await create_user_and_project(client)
    missing_project_id = str(uuid.uuid4())

    response = await client.post(
        "/api/v1/ai/requests",
        json=metering_payload(user["id"], missing_project_id),
    )

    assert response.status_code == 404
    assert response.json() == {
        "code": "project_not_found",
        "message": "Project not found.",
        "detail": {"project_id": missing_project_id},
    }


@pytest.mark.asyncio
async def test_negative_token_value_returns_422(client):
    user, project = await create_user_and_project(client)
    payload = metering_payload(user["id"], project["id"])
    payload["prompt_tokens"] = -1

    response = await client.post("/api/v1/ai/requests", json=payload)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_empty_provider_model_status_returns_422(client):
    user, project = await create_user_and_project(client)
    payload = metering_payload(user["id"], project["id"])
    payload["provider"] = ""
    payload["model"] = ""
    payload["status"] = ""

    response = await client.post("/api/v1/ai/requests", json=payload)

    assert response.status_code == 422

