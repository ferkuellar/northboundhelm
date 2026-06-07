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

