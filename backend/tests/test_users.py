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


@pytest.mark.asyncio
async def test_duplicate_user_email_returns_409(client):
    payload = {
        "email": "duplicate@example.com",
        "name": "Duplicate User",
        "role": "developer",
    }

    first_response = await client.post("/api/v1/users", json=payload)
    duplicate_response = await client.post("/api/v1/users", json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {
        "code": "user_email_exists",
        "message": "A user with this email already exists.",
        "detail": {"email": "duplicate@example.com"},
    }


@pytest.mark.asyncio
async def test_invalid_user_payload_returns_422(client):
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "not-an-email",
            "name": "",
        },
    )

    assert response.status_code == 422
