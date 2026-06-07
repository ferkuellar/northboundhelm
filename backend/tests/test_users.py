import pytest


@pytest.mark.asyncio
async def test_create_and_list_users(client):
    create_response = await client.post(
        "/api/v1/users",
        json={
            "email": "developer@example.com",
            "name": "Developer Example",
            "role": "developer",
        },
    )

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["email"] == "developer@example.com"
    assert created["role"] == "developer"

    list_response = await client.get("/api/v1/users")
    assert list_response.status_code == 200
    users = list_response.json()
    assert len(users) == 1
    assert users[0]["email"] == "developer@example.com"

