# Architecture

Northbound Helm Sprint 001 provides a single FastAPI service backed by PostgreSQL.

The API mounts Sprint 001 routes under `/api/v1`. SQLAlchemy async sessions are provided through a FastAPI dependency. Alembic owns schema creation and migration.

