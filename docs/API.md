# API

Northbound Helm exposes Sprint 002 backend endpoints under `/api/v1`.

Error responses for duplicate resources use a stable JSON contract:

```json
{
  "code": "machine_readable_code",
  "message": "Human readable message.",
  "detail": {}
}
```

## Health

### `GET /api/v1/health`

Purpose: confirm the API process and database connection are available.

Success: `200 OK`

```json
{
  "status": "ok",
  "database": "ok"
}
```

Database check failures are not masked by Sprint 002. If the database query fails, FastAPI returns its normal server error response.

## Users

### `GET /api/v1/users`

Purpose: list users ordered by creation time and email.

Success: `200 OK`

Response body:

```json
[
  {
    "id": "uuid",
    "email": "developer@example.com",
    "name": "Developer Example",
    "role": "developer",
    "org_id": "default",
    "is_active": true,
    "created_at": "2026-06-07T00:00:00Z"
  }
]
```

### `POST /api/v1/users`

Purpose: create a user. Production authentication is out of scope for Sprint 002.

Request body:

```json
{
  "email": "developer@example.com",
  "name": "Developer Example",
  "role": "developer",
  "org_id": "default",
  "is_active": true
}
```

Success: `201 Created`

Duplicate email: `409 Conflict`

```json
{
  "code": "user_email_exists",
  "message": "A user with this email already exists.",
  "detail": {
    "email": "admin@northboundhelm.io"
  }
}
```

Schema validation failure: `422 Unprocessable Entity`

## Projects

### `GET /api/v1/projects`

Purpose: list projects ordered by creation time and name.

Success: `200 OK`

Response body:

```json
[
  {
    "id": "uuid",
    "name": "FONDIXPAY",
    "org_id": "default",
    "owner_id": "uuid",
    "budget_usd": "5000.00",
    "description": "FinOps project for FONDIXPAY.",
    "is_active": true,
    "created_at": "2026-06-07T00:00:00Z"
  }
]
```

### `POST /api/v1/projects`

Purpose: create a project.

Request body:

```json
{
  "name": "FONDIXPAY",
  "org_id": "default",
  "owner_id": null,
  "budget_usd": "5000.00",
  "description": "FinOps project for FONDIXPAY.",
  "is_active": true
}
```

Success: `201 Created`

Duplicate project name within the same `org_id`: `409 Conflict`

```json
{
  "code": "project_name_exists",
  "message": "A project with this name already exists.",
  "detail": {
    "name": "FONDIXPAY"
  }
}
```

Schema validation failure: `422 Unprocessable Entity`

## Status Codes

- `200 OK`: successful reads.
- `201 Created`: successful creates.
- `409 Conflict`: duplicate user email or duplicate project name within an org.
- `422 Unprocessable Entity`: request body fails Pydantic validation.
