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

Status: ACCEPTED

Evidence:
- pytest tests/ -v: 7 passed in 0.21s
- health: `{"status":"ok","database":"ok"}`
- docs: HTTP/1.1 200 OK
- user create: 201
- user duplicate: 409 user_email_exists
- user invalid payload: 422
- project create: 201
- project duplicate: 409 project_name_exists
- project invalid payload: 422
- docker compose regression: api running, postgres healthy
- alembic upgrade head: Context impl PostgresqlImpl; Will assume transactional DDL; no migration errors
- seed idempotent: reused admin/developer users and FONDIXPAY/Northbound Demo/Internal Tools projects; seed completed

Notes:
- No authentication, AI gateway, provider calls, frontend, cloud infrastructure, or new tables were added.
- Duplicate project validation remains scoped to `name` plus `org_id`.

## Sprint 003 - Metering Foundation

Status: ACCEPTED

Evidence:
- pytest tests/ -v: 13 passed in 0.45s
- health: `{"status":"ok","database":"ok"}`
- docs: HTTP/1.1 200 OK
- ai request create: 201
- ai request list: 200
- ai request detail: 200
- ai request missing detail: 404 ai_request_not_found
- unknown user: 404 user_not_found
- unknown project: 404 project_not_found
- invalid token payload: 422
- empty provider/model/status: 422
- total_tokens calculation: 1000 + 500 = 1500
- docker compose regression: api rebuilt/running, postgres healthy
- alembic upgrade head: Context impl PostgresqlImpl; Will assume transactional DDL; no migration errors
- seed idempotent: reused admin/developer users and FONDIXPAY/Northbound Demo/Internal Tools projects; seed completed

Notes:
- AI request records are internal/manual metering events only.
- No OpenAI, Anthropic, Gemini, Mistral, proxy, streaming, rate limiting, budget enforcement, dashboard, frontend, or cloud infrastructure was added.
- `estimated_cost` is stored as provided by the request for Sprint 003.

## Sprint 004 - Usage Query API

Status: ACCEPTED

Evidence:
- pytest tests/ -v: 21 passed in 1.06s
- health: `{"status":"ok","database":"ok"}`
- docs: HTTP/1.1 200 OK
- usage by project: 200
- usage by user: 200
- usage by model: 200
- project aggregation totals: request_count 2, prompt_tokens 300, completion_tokens 150, total_tokens 450, estimated_cost 0.003000
- user aggregation totals: request_count 2, prompt_tokens 300, completion_tokens 150, total_tokens 450, estimated_cost 0.003000
- model aggregation totals: request_count 2, prompt_tokens 300, completion_tokens 150, total_tokens 450, estimated_cost 0.003000
- empty filter result: 200 []
- invalid UUID filter: 422
- invalid datetime filter: 422
- docker compose regression: api running, postgres healthy
- alembic upgrade head: Context impl PostgresqlImpl; Will assume transactional DDL; no migration errors
- seed idempotent: reused admin/developer users and FONDIXPAY/Northbound Demo/Internal Tools projects; seed completed

Notes:
- Usage endpoints aggregate existing `ai_requests` records only.
- No budgets, alerts, dashboard, provider calls, forecasting, recommendations, auth, new tables, packages, cloud, or observability were added.

## Sprint 005 - Budget Foundation

Status: IMPLEMENTED / NEEDS REVIEW

Evidence:
- pytest tests/ -v: 28 passed in 2.24s
- health: `{"status":"ok","database":"ok"}`
- docs: HTTP/1.1 200 OK
- budget create: 201
- budget duplicate update: 200
- budget list: 200
- budget status: 200
- status ok: spent 1.00, consumed_pct 5.00, status ok
- status warning: spent 8.00, consumed_pct 80.00, status warning
- status exceeded: spent 10.00, consumed_pct 100.00, status exceeded
- unknown project: 404 project_not_found
- invalid period: 422
- invalid amount: 422
- invalid alert threshold: 422
- invalid UUID filter: 422
- docker compose regression: api running, postgres healthy
- alembic upgrade head: Context impl PostgresqlImpl; Will assume transactional DDL; no migration errors
- seed idempotent: reused admin/developer users and FONDIXPAY/Northbound Demo/Internal Tools projects; seed completed

Notes:
- Budget records use the existing `budgets` table.
- Budget status is calculated from existing `ai_requests.estimated_cost` values for the current month or current year.
- `project_id` plus `period` upsert behavior is enforced in the service layer without adding a migration.
- No notifications, alerts, billing, invoicing, auth, frontend, provider calls, cloud infrastructure, new packages, or new tables were added.
