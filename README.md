# Northbound Helm

Sprint 001 backend foundation for Northbound Helm.

## Stack

- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.x async
- Alembic
- Pydantic v2
- pytest

## Local Docker Run

```bash
docker compose -f infra/docker-compose.yml up -d
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec api python -m app.seed
curl http://localhost:8000/api/v1/health
```

Swagger UI is available at:

```text
http://localhost:8000/docs
```

## Local Backend Tests

```bash
cd backend
pytest tests/ -v
```

