# HARNESS.md — Northbound Helm MVP Control Harness

## Purpose

This file controls scope, sprint sequencing, acceptance gates, validation evidence, and stop conditions for  **Northbound Helm** .

Northbound Helm must not become an endless architecture experiment.

This harness exists to keep the project:

* Finite
* Verifiable
* Testable
* Demo-oriented
* Cost-controlled
* Safe from scope creep
* Useful before it becomes complex

The project must build toward a closed MVP in  **10 sprints maximum** .

After Sprint 010, development stops for executive review unless the user explicitly approves a new phase.

---

## Project Identity

**Project:** Northbound Helm
**Product type:** AI FinOps and Governance Control Plane
**Core purpose:** Record, measure, analyze, and govern AI token consumption and estimated cost.
**Backend stack:** FastAPI, PostgreSQL, SQLAlchemy 2.x async, Alembic, Pydantic v2
**Local runtime:** Docker Compose
**Current MVP target:** Backend-only operational MVP

Northbound Helm is not yet a full SaaS platform.

Until Sprint 010 is accepted, it is a controlled backend MVP.

---

## Source of Truth Order

When instructions conflict, follow this order:

1. `HARNESS.md`
2. `AGENTS.md`
3. `planning/STATE.md`
4. `planning/DECISIONS.md`
5. Active sprint folder:
   * `requirements.md`
   * `blueprint.md`
   * `acceptance.md`
   * `handoff-prompt.md`
6. Durable docs:
   * `docs/API.md`
   * `docs/DATA_MODEL.md`
   * `docs/ARCHITECTURE.md`
7. Existing code and tests

If a requested change conflicts with this harness, the Builder must stop and report the conflict.

---

## Non-Negotiable Rules

### Rule 1 — No Scope Creep

If a feature is not listed in the active sprint scope, it is not built.

The Builder may suggest follow-up work, but must not silently implement it.

### Rule 2 — No Acceptance Without Evidence

A sprint is not accepted because code exists.

A sprint is accepted only when the user receives command evidence proving:

* Tests passed.
* Docker still works.
* Alembic still works.
* Seed still works.
* Health endpoint still works.
* Swagger still loads.
* Sprint-specific API behavior works.
* Documentation was updated.
* No out-of-scope work was added.

### Rule 3 — User Accepts, Builder Does Not

The Builder may mark a sprint as:

```text
IMPLEMENTED / NEEDS REVIEW
```

Only the user may mark a sprint as:

```text
ACCEPTED
```

### Rule 4 — No Provider Spend Without Approval

No real OpenAI, Anthropic, Gemini, Mistral, or other paid provider call may be added before the sprint that explicitly authorizes it.

Provider API keys must never be hardcoded.

Real provider calls must be disabled by default until approved.

### Rule 5 — No Frontend Before MVP Backend Review

Do not build the Next.js dashboard before Sprint 010 is accepted.

Swagger and API docs are enough for the backend MVP.

### Rule 6 — No Cloud Before Local MVP

Do not add AWS, ECS, RDS, Terraform, Kubernetes, Helm charts, CI/CD pipelines, production observability, or cloud networking before Sprint 010.

Docker Compose is the only required runtime for the MVP.

### Rule 7 — No Auth Expansion Until Scheduled

Do not implement JWT, OAuth2, RBAC, API keys, user sessions, refresh tokens, or enterprise auth unless a sprint explicitly includes it.

### Rule 8 — No New Packages Without Justification

Do not install or add new dependencies unless:

1. The sprint explicitly requires it.
2. The package is necessary.
3. The Builder reports why.
4. The user approves.

### Rule 9 — No Data Model Drift

Do not add tables or major columns unless the sprint explicitly requires it.

If a bug requires a migration, the Builder must explain:

* What is broken.
* Why a model change is required.
* What migration will be created.
* How rollback works.

### Rule 10 — The Project Stops at Sprint 010

Sprint 011 does not exist by default.

Sprint 011 requires a deliberate continuation decision.

---

## Closed MVP Roadmap

Northbound Helm MVP is limited to the following 10 sprints.

| Sprint | Name                       | Status   | Purpose                                             |
| -----: | -------------------------- | -------- | --------------------------------------------------- |
|    001 | Foundation                 | ACCEPTED | Backend, DB, migration, seed, Docker, health, tests |
|    002 | API Contract Hardening     | ACCEPTED | Harden users/projects/health contracts              |
|    003 | Metering Foundation        | ACCEPTED | Record internal AI request usage events             |
|    004 | Usage Query API            | ACCEPTED | Query usage by project, user, and model             |
|    005 | Budget Foundation          | ACCEPTED | Manage budgets and calculate budget status          |
|    006 | Alerts Foundation          | PLANNED  | Generate internal budget threshold alerts           |
|    007 | AI Gateway Mock Proxy      | PLANNED  | Simulate gateway flow without external providers    |
|    008 | Provider Adapter Interface | PLANNED  | Add provider abstraction and mock provider          |
|    009 | OpenAI Adapter MVP         | PLANNED  | Add first controlled real provider adapter          |
|    010 | MVP Readiness Review       | PLANNED  | Audit, stabilize, document, and decide next phase   |

No sprint may be inserted between these without updating this harness and user approval.

---

## Explicitly Forbidden Before Sprint 010

The following are blocked until after Sprint 010 acceptance:

```text
Frontend Next.js dashboard
Mobile app
AWS deployment
Terraform
ECS/Fargate
RDS production setup
Kubernetes
Helm charts
CI/CD pipelines
GitHub Actions deployment workflows
Prometheus
Grafana
Loki
OpenTelemetry production stack
Multi-tenant enterprise model
Advanced RBAC
Enterprise SSO
Stripe or payments
Marketplace
Autonomous agents
Claude/Gemini/Mistral adapters
Streaming completions
Embeddings
RAG
Vector database
Billing system
Customer portal
Production email notifications
Slack/Teams notifications
```

If the Builder attempts to add any of these, the sprint fails.

---

## Sprint Gate Template

Every sprint must pass these gates.

### Gate 1 — Preflight

Before code changes, the Builder must report:

```text
Current sprint:
Files inspected:
Existing behavior:
Expected files to modify:
Expected tests:
Blockers or ambiguities:
Out-of-scope items avoided:
```

No implementation should begin before the user approves or the prompt explicitly allows proceeding.

### Gate 2 — Implementation

During implementation, the Builder must:

* Keep changes within scope.
* Avoid unrelated refactors.
* Preserve previous sprint behavior.
* Update or add tests.
* Update relevant docs.
* Avoid new dependencies unless approved.

### Gate 3 — Validation

The Builder must run:

```powershell
.\.venv\Scripts\pytest tests/ -v
```

And, when Docker is part of the sprint:

```powershell
docker compose -f infra/docker-compose.yml up -d --build
docker compose -f infra/docker-compose.yml exec api alembic upgrade head
docker compose -f infra/docker-compose.yml exec api python -m app.seed
curl.exe http://localhost:8000/api/v1/health
curl.exe -I http://localhost:8000/docs
```

Expected baseline:

```json
{"status":"ok","database":"ok"}
```

Swagger expected:

```text
HTTP/1.1 200 OK
```

### Gate 4 — Evidence Report

The Builder must report:

```text
Tests:
Docker:
Alembic:
Seed:
Health:
Swagger:
Sprint-specific contract checks:
Files created:
Files modified:
Git status:
Risks:
Out-of-scope confirmation:
Suggested commit:
```

### Gate 5 — User Acceptance

The user decides:

```text
ACCEPTED
REJECTED
NEEDS FIXES
```

The Builder must not self-accept.

---

## Standard Validation Evidence

Minimum evidence for every sprint:

```text
pytest tests/ -v
X passed

curl http://localhost:8000/api/v1/health
{"status":"ok","database":"ok"}

curl -I http://localhost:8000/docs
HTTP/1.1 200 OK
```

If a sprint adds API behavior, direct API contract checks are required.

Example:

```text
POST endpoint success -> expected status code
Duplicate case -> expected status code
Invalid payload -> expected status code
Not found case -> expected status code
```

No sprint is complete with only “tests passed.”

---

## Sprint 001 — Foundation

### Status

```text
ACCEPTED
```

### Purpose

Create the working backend foundation.

### Accepted Evidence

Required evidence included:

```text
pytest tests/ -v
health endpoint
Swagger docs
Alembic migration
Docker Compose
Seed idempotency
```

### Commit

```text
sprint-001: create backend foundation with migrations seed and tests
docs: mark sprint 001 accepted
```

---

## Sprint 002 — API Contract Hardening

### Status

```text
IMPLEMENTED / NEEDS REVIEW
```

### Purpose

Harden users, projects, and health endpoint contracts.

### Acceptance Evidence Required

```text
pytest tests/ -v
health endpoint returns status/database ok
Swagger returns 200
POST /api/v1/users create -> 201
POST /api/v1/users duplicate -> 409
POST /api/v1/users invalid -> 422
POST /api/v1/projects create -> 201
POST /api/v1/projects duplicate -> 409
POST /api/v1/projects invalid -> 422
Docker regression passes
Alembic upgrade passes
Seed remains idempotent
docs/API.md updated
docs/DATA_MODEL.md updated
planning/STATE.md updated
```

### Commit

```text
sprint-002: harden api contracts and crud validation
```

---

## Sprint 003 — Metering Foundation

### Status

```text
PLANNED
```

### Purpose

Build the internal usage metering foundation using the existing `ai_requests` table.

### Scope

Allowed:

```text
POST /api/v1/ai/requests
GET /api/v1/ai/requests
GET /api/v1/ai/requests/{request_id}
Pydantic schemas for ai_requests
Metering service layer
Validation of user_id and project_id
Validation of tokens/provider/model/status
Auto-calculation of total_tokens
Tests for success and failure paths
API and data model documentation
```

Not allowed:

```text
Real OpenAI calls
Real Anthropic calls
Real Gemini/Mistral calls
Proxying to external providers
API key auth
JWT auth
Budget enforcement
Alerts
Frontend
Cloud deployment
New tables unless bug-approved
New packages
```

### Required Evidence

```text
POST /api/v1/ai/requests -> 201
GET /api/v1/ai/requests -> 200
GET /api/v1/ai/requests/{id} -> 200
unknown user -> 404
unknown project -> 404
unknown request -> 404
negative token payload -> 422
empty provider/model/status -> 422
total_tokens calculated correctly
pytest tests/ -v passes
Docker regression passes
Alembic upgrade passes
Seed idempotent
Health ok
Swagger ok
```

### Commit

```text
sprint-003: add ai request metering foundation
```

---

## Sprint 004 — Usage Query API

### Status

```text
PLANNED
```

### Purpose

Expose usage aggregation over existing `ai_requests`.

### Scope

Allowed endpoints:

```text
GET /api/v1/usage/by-project
GET /api/v1/usage/by-user
GET /api/v1/usage/by-model
```

Allowed behavior:

```text
Aggregate total_tokens
Aggregate estimated_cost
Group by project/user/model
Filter by date range
Filter by provider/model/status
Return empty results safely
Test aggregation correctness
Document API
```

Not allowed:

```text
Budget enforcement
Alerts
Dashboard
Provider calls
Complex analytics
Forecasting
FinOps recommendations
```

### Commit

```text
sprint-004: add usage query api
```

---

## Sprint 005 — Budget Foundation

### Status

```text
PLANNED
```

### Purpose

Enable project budget tracking.

### Scope

Allowed:

```text
GET /api/v1/budgets
POST /api/v1/budgets
GET /api/v1/budgets/status
Create/update budget records
Calculate spend from ai_requests
Calculate consumed percentage
Return ok/warning/exceeded status
Tests
Documentation
```

Not allowed:

```text
Automatic notifications
Payment billing
Customer invoicing
External integrations
```

### Commit

```text
sprint-005: add budget foundation
```

---

## Sprint 006 — Alerts Foundation

### Status

```text
PLANNED
```

### Purpose

Generate internal budget threshold alerts.

### Scope

Allowed:

```text
GET /api/v1/alerts
Internal alert calculation based on budgets and usage
Alert status: active/resolved if model already supports it
Tests
Documentation
```

Not allowed:

```text
Email notifications
Slack notifications
Teams notifications
WhatsApp notifications
PagerDuty
Background workers
```

### Commit

```text
sprint-006: add alerts foundation
```

---

## Sprint 007 — AI Gateway Mock Proxy

### Status

```text
PLANNED
```

### Purpose

Create the gateway contract without calling real AI providers.

### Scope

Allowed:

```text
POST /api/v1/ai/request
Mock provider response
Simulated token usage
Simulated estimated cost
Persist metering record
Return mock completion
Tests
Documentation
```

Not allowed:

```text
Real provider calls
Streaming
Tool calling
Embeddings
RAG
API key enforcement
```

### Commit

```text
sprint-007: add mock ai gateway proxy
```

---

## Sprint 008 — Provider Adapter Interface

### Status

```text
PLANNED
```

### Purpose

Create the clean provider abstraction before real providers.

### Scope

Allowed:

```text
backend/app/providers/base.py
backend/app/providers/mock_provider.py
backend/app/providers/factory.py
Provider interface
Mock provider implementation
Standard provider response object
Standard provider error object
Tests
Documentation
```

Not allowed:

```text
OpenAI real adapter
Anthropic real adapter
Gemini real adapter
Provider-specific billing complexity
```

### Commit

```text
sprint-008: add provider adapter interface
```

---

## Sprint 009 — OpenAI Adapter MVP

### Status

```text
PLANNED
```

### Purpose

Add the first controlled real AI provider adapter.

### Scope

Allowed:

```text
OpenAI adapter only
Environment-based API key
Disabled by default unless env flag enables it
Timeout handling
Provider error handling
Usage extraction if available
Cost calculation using documented internal pricing table or placeholder config
Tests using mocks only
Documentation
```

Not allowed:

```text
Anthropic
Gemini
Mistral
Streaming
Tools/function calling
Embeddings
Vision
Real API tests in CI
Hardcoded API keys
```

### Commit

```text
sprint-009: add openai adapter mvp
```

---

## Sprint 010 — MVP Readiness Review

### Status

```text
PLANNED
```

### Purpose

Stop building and evaluate whether the MVP is real, stable, and worth continuing.

### Scope

Allowed:

```text
Audit all endpoints
Run full test suite
Run Docker validation
Review migrations
Review docs
Review risks
Review security gaps
Create MVP demo script
Create continuation recommendation
Create stop/go decision document
```

Not allowed:

```text
New product features
Frontend
Cloud deployment
New providers
Auth expansion
Dashboard
```

### Required Output

Create:

```text
docs/MVP_READINESS_REVIEW.md
```

It must conclude with one of:

```text
A) READY FOR INTERNAL DEMO
B) NEEDS STABILIZATION SPRINT
C) STOP BUILDING UNTIL PRODUCT VALIDATION
```

### Commit

```text
sprint-010: complete mvp readiness review
```

---

## Required STATE.md Format

At the end of each sprint, `planning/STATE.md` must include:

```text
# Project State — Northbound Helm

## Current Sprint

Sprint XXX - Name

## Status

IMPLEMENTED / NEEDS REVIEW

## Evidence

- pytest:
- docker:
- alembic:
- seed:
- health:
- swagger:
- sprint-specific checks:

## Files Changed

- ...

## Risks

- ...

## Next Recommended Action

- User review and acceptance.
```

After user acceptance, update status to:

```text
ACCEPTED
```

---

## Required Final Report Format

Every Builder final report must use this format:

```text
# Sprint XXX Final Report

## Summary

## Files Created

## Files Modified

## Validation Evidence

### Tests

### Docker

### Alembic

### Seed

### Health

### Swagger

### Sprint-Specific API Checks

## Out-of-Scope Confirmation

## Risks / Limitations

## Git Status

## Suggested Commit

## Acceptance Status

IMPLEMENTED / NEEDS REVIEW
```

If any validation is missing, the Builder must say:

```text
NOT READY FOR ACCEPTANCE
```

---

## Stop Conditions

Stop immediately if any of these occur:

### Technical Stop

```text
Tests cannot run
Docker cannot start
Alembic cannot upgrade
Database schema becomes inconsistent
Health endpoint fails
Swagger fails
A migration is destructive without approval
```

### Scope Stop

```text
Builder attempts to add frontend
Builder attempts to add cloud infra
Builder attempts to add auth outside sprint
Builder attempts to call real providers before Sprint 009
Builder adds new packages without approval
Builder changes data model outside approved scope
```

### Product Stop

```text
Sprint 010 review shows no clear demo value
The project requires more than 10 MVP sprints
The system cannot explain its value in one minute
The system cannot produce measurable AI spend/usage evidence
```

---

## Severity Model

Use this severity model for findings:

```text
SEV-1 Critical
Production blocker, data loss risk, broken migrations, exposed secrets, broken health, broken Docker.

SEV-2 High
Major API behavior broken, wrong cost/token recording, invalid budget calculations, missing required validation.

SEV-3 Medium
Incomplete tests, weak documentation, inconsistent error shape, incomplete edge cases.

SEV-4 Low
Naming, formatting, cleanup, minor docs inconsistency.

SEV-5 Enhancement
Future improvement outside MVP scope.
```

SEV-1 and SEV-2 block sprint acceptance.

---

## Cost Control Rules

Northbound Helm is an AI FinOps product. It must not create uncontrolled AI costs while being built.

Before Sprint 009:

```text
No real provider calls.
No live API spending.
No provider credentials required.
```

At Sprint 009:

```text
Real provider adapter must be disabled by default.
API key must come from environment.
Tests must mock provider calls.
No automated test may spend provider credits.
Manual live call requires explicit user approval.
```

---

## Security Rules

Always enforce:

```text
No secrets in code.
No .env committed.
No API keys in tests.
No sensitive prompt/completion content stored unless explicitly approved.
No raw provider payloads with secrets logged.
No auth expansion outside planned sprint.
```

The `ai_requests.metadata` field may store non-sensitive provider metadata only.

---

## Documentation Rules

Every sprint that changes behavior must update:

```text
docs/API.md
docs/DATA_MODEL.md if data behavior changes
planning/STATE.md
```

Architecture changes must update:

```text
docs/ARCHITECTURE.md
```

Important decisions must update:

```text
planning/DECISIONS.md
```

Risks must update:

```text
planning/RISKS.md
```

---

## Commit Rules

Use one clean commit per accepted sprint when practical.

Commit format:

```text
sprint-XXX: short imperative description
```

Examples:

```text
sprint-003: add ai request metering foundation
sprint-004: add usage query api
sprint-005: add budget foundation
```

Documentation-only acceptance commits may use:

```text
docs: mark sprint XXX accepted
```

---

## MVP Definition of Done

Northbound Helm MVP is done only when all are true:

```text
Sprint 001 accepted
Sprint 002 accepted
Sprint 003 accepted
Sprint 004 accepted
Sprint 005 accepted
Sprint 006 accepted
Sprint 007 accepted
Sprint 008 accepted
Sprint 009 accepted
Sprint 010 accepted
Full test suite passes
Docker Compose works
Alembic upgrade works
Seed is idempotent
Health returns status/database ok
Swagger loads
MVP readiness review exists
No forbidden scope was added
```

---

## Post-MVP Rule

After Sprint 010, stop.

Possible next-phase decisions:

```text
A) Build frontend dashboard
B) Add auth/security layer
C) Deploy to AWS
D) Add Anthropic/Gemini
E) Add production observability
F) Pause and validate with users
G) Kill or pivot the product
```

No next phase starts automatically.

---

## Operator Reminder

This project is not judged by how much code it accumulates.

It is judged by whether it can prove:

```text
Who used AI?
For what project?
On what provider/model?
How many tokens?
At what estimated cost?
Against what budget?
With what alert risk?
Through what controlled gateway?
```

If a sprint does not move the project closer to answering those questions, it does not belong in the MVP.
