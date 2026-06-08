# API

Northbound Helm exposes backend endpoints under `/api/v1`.

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

## AI Request Metering

Sprint 003 adds internal metering records only. These endpoints do not call OpenAI, Anthropic, Gemini, Mistral, or any other external provider.

### `POST /api/v1/ai/requests`

Purpose: record an AI usage event in `ai_requests`.

Request body:

```json
{
  "user_id": "uuid",
  "project_id": "uuid",
  "provider": "openai",
  "model": "gpt-4o",
  "prompt_tokens": 1000,
  "completion_tokens": 500,
  "estimated_cost": "0.005000",
  "latency_ms": 1200,
  "status": "success",
  "metadata": {
    "environment": "local",
    "source": "manual_test"
  }
}
```

Success: `201 Created`

Response body:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "project_id": "uuid",
  "provider": "openai",
  "model": "gpt-4o",
  "prompt_tokens": 1000,
  "completion_tokens": 500,
  "total_tokens": 1500,
  "estimated_cost": "0.005000",
  "latency_ms": 1200,
  "status": "success",
  "metadata": {
    "environment": "local",
    "source": "manual_test"
  },
  "created_at": "2026-06-07T00:00:00Z"
}
```

Behavior:
- `total_tokens` is calculated as `prompt_tokens + completion_tokens`.
- Optional `metadata` is stored in the PostgreSQL `metadata` column through the model's safe `request_metadata` Python attribute.
- `estimated_cost` is stored as supplied by the client for Sprint 003.

Unknown user: `404 Not Found`

```json
{
  "code": "user_not_found",
  "message": "User not found.",
  "detail": {
    "user_id": "uuid"
  }
}
```

Unknown project: `404 Not Found`

```json
{
  "code": "project_not_found",
  "message": "Project not found.",
  "detail": {
    "project_id": "uuid"
  }
}
```

Schema validation failure: `422 Unprocessable Entity`

### `GET /api/v1/ai/requests`

Purpose: list recorded AI request metering events.

Success: `200 OK`

Optional filters:
- `project_id`
- `user_id`
- `provider`
- `model`
- `status`

### `GET /api/v1/ai/requests/{request_id}`

Purpose: return one metering record by ID.

Success: `200 OK`

Missing request: `404 Not Found`

```json
{
  "code": "ai_request_not_found",
  "message": "AI request not found.",
  "detail": {
    "request_id": "uuid"
  }
}
```

## Usage Query API

Sprint 004 aggregates existing `ai_requests` records. It does not enforce budgets, generate alerts, call providers, forecast spend, or produce FinOps recommendations.

Shared optional query parameters:
- `start_date`: filter `ai_requests.created_at >= start_date`
- `end_date`: filter `ai_requests.created_at <= end_date`
- `provider`
- `model`
- `status`
- `project_id`
- `user_id`

Invalid UUID or datetime query parameters return `422 Unprocessable Entity`.

### `GET /api/v1/usage/by-project`

Purpose: return usage aggregated by project.

Success: `200 OK`

Response body:

```json
[
  {
    "project_id": "uuid",
    "project_name": "FONDIXPAY",
    "request_count": 3,
    "prompt_tokens": 3000,
    "completion_tokens": 1500,
    "total_tokens": 4500,
    "estimated_cost": "0.015000"
  }
]
```

No matching rows return:

```json
[]
```

### `GET /api/v1/usage/by-user`

Purpose: return usage aggregated by user.

Success: `200 OK`

Response body:

```json
[
  {
    "user_id": "uuid",
    "user_email": "developer1@northboundhelm.io",
    "user_name": "Developer One",
    "request_count": 3,
    "prompt_tokens": 3000,
    "completion_tokens": 1500,
    "total_tokens": 4500,
    "estimated_cost": "0.015000"
  }
]
```

No matching rows return:

```json
[]
```

### `GET /api/v1/usage/by-model`

Purpose: return usage aggregated by provider and model.

Success: `200 OK`

Response body:

```json
[
  {
    "provider": "openai",
    "model": "gpt-4o",
    "request_count": 3,
    "prompt_tokens": 3000,
    "completion_tokens": 1500,
    "total_tokens": 4500,
    "estimated_cost": "0.015000"
  }
]
```

No matching rows return:

```json
[]
```

## Status Codes

- `200 OK`: successful reads.
- `201 Created`: successful creates.
- `409 Conflict`: duplicate user email or duplicate project name within an org.
- `404 Not Found`: unknown referenced user, project, or AI request.
- `422 Unprocessable Entity`: request body fails Pydantic validation.
