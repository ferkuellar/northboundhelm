# Northbound Helm Agent Instructions

Northbound Helm Sprint 001 is a FastAPI + PostgreSQL + SQLAlchemy 2.x async backend foundation.

## Frozen Scope

- FastAPI backend only.
- PostgreSQL 16.
- SQLAlchemy 2.x async.
- Alembic migrations.
- Pydantic v2 schemas.
- Docker Compose with `api` and `postgres`.
- CRUD endpoints for users and projects.
- Health endpoint at `/api/v1/health`.
- Seed script at `backend/app/seed.py`.
- Swagger UI at `/docs`.

## Constraints

- Do not touch `C:\Users\ferna\OneDrive\Escritorio\NorthbopundFinOps`.
- Do not use MongoDB or Motor.
- Do not add frontend work.
- Do not add Kubernetes, AWS, Terraform, ECS, or cloud config.
- Do not implement AI gateway calls.
- Do not implement production auth.
- Do not claim completion without command evidence.

