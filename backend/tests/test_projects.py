import pytest


@pytest.mark.asyncio
async def test_create_and_list_projects(client):
    create_response = await client.post(
        "/api/v1/projects",
        json={
            "name": "Northbound Demo",
            "org_id": "default",
            "budget_usd": "1500.00",
            "description": "Demo project",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "Northbound Demo"
    assert created["org_id"] == "default"

    list_response = await client.get("/api/v1/projects")
    assert list_response.status_code == 200
    projects = list_response.json()
    assert len(projects) == 1
    assert projects[0]["name"] == "Northbound Demo"


@pytest.mark.asyncio
async def test_duplicate_project_name_in_same_org_returns_409(client):
    payload = {
        "name": "FONDIXPAY",
        "org_id": "default",
        "budget_usd": "5000.00",
    }

    first_response = await client.post("/api/v1/projects", json=payload)
    duplicate_response = await client.post("/api/v1/projects", json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "code": "project_name_exists",
        "message": "A project with this name already exists.",
        "detail": {"name": "FONDIXPAY"},
    }


@pytest.mark.asyncio
async def test_invalid_project_payload_returns_422(client):
    response = await client.post(
        "/api/v1/projects",
        json={
            "name": "",
            "budget_usd": "-1.00",
        },
    )

    assert response.status_code == 422
