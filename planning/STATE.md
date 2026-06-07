# Northbound Helm State

## Sprint 001 - Foundation

Status: ACCEPTED

Evidence:
- `pytest tests/ -v`: 3 passed
- `/api/v1/health`: status ok, database ok
- `/docs`: 200 OK
- `alembic upgrade head`: clean
- `docker compose`: api/postgres running
- `python -m app.seed`: idempotent

Accepted risks:
- Seed password hashing is local/demo only. Production authentication is out of scope for Sprint 001.
- Unit tests use SQLite async for speed. PostgreSQL was validated through Docker, Alembic, and health checks.

Next recommended sprint: Sprint 002 - API Contract Hardening + CRUD Validation.

## Sprint 002 - API Contract Hardening

Status: IMPLEMENTED / NEEDS REVIEW

Evidence:
- `pytest tests/ -v`: 7 passed
- `/api/v1/health`: `{"status":"ok","database":"ok"}`
- `/docs`: 200 OK
- Docs updated: `docs/API.md`, `docs/DATA_MODEL.md`
- Duplicate user email: 409 with `user_email_exists`
- Duplicate project name within `org_id`: 409 with `project_name_exists`
- Invalid user payload: 422
- Invalid project payload: 422
- Successful user/project creates: 201
- `alembic upgrade head`: clean in Docker API container
- `python -m app.seed`: idempotent in Docker API container

Notes:
- No authentication, AI gateway, provider calls, frontend, cloud infrastructure, or new tables were added.
- Duplicate project validation remains scoped to `name` plus `org_id`.
