# Data Model

Sprint 003 keeps the Sprint 001 schema unchanged and starts using `ai_requests` for internal metering records.

## `users`

Primary key:
- `id` UUID

Important columns:
- `email` unique, indexed, required
- `name` required
- `role` required
- `org_id` required
- `is_active` required
- `hashed_password` nullable, only used by local seed data
- `created_at` required

## `projects`

Primary key:
- `id` UUID

Foreign keys:
- `owner_id` references `users.id`

Important columns:
- `name` required
- `org_id` required
- `budget_usd` numeric
- `description` nullable
- `is_active` required
- `created_at` required

Important constraints:
- Unique project name within `org_id` via `uq_projects_name_org_id`

## `ai_requests`

Primary key:
- `id` UUID

Foreign keys:
- `user_id` references `users.id`
- `project_id` references `projects.id`

Important columns:
- `provider` required provider label, stored as client-supplied text
- `model` required model label, stored as client-supplied text
- `prompt_tokens` non-negative prompt token count
- `completion_tokens` non-negative completion token count
- `total_tokens` calculated as `prompt_tokens + completion_tokens` by the Sprint 003 service
- `estimated_cost` numeric cost supplied by the client for Sprint 003
- `latency_ms` optional non-negative latency
- `status` required status label, stored as client-supplied text
- `metadata` JSONB in PostgreSQL
- `created_at` required timestamp

Metadata handling:
- SQLAlchemy reserves the Python attribute name `metadata`, so the model uses `request_metadata`.
- The database column remains named `metadata`.
- The public API request/response field remains `metadata`.

Important indexes:
- `ix_ai_requests_project_created_at` on `project_id`, `created_at`
- `ix_ai_requests_user_created_at` on `user_id`, `created_at`
- `ix_ai_requests_provider_model_created_at` on `provider`, `model`, `created_at`
- `ix_ai_requests_status_created_at` on `status`, `created_at`

## `budgets`

Primary key:
- `id` UUID

Foreign keys:
- `project_id` references `projects.id`

Important columns:
- `period`
- `amount_usd`
- `alert_at_pct`
- `created_at`

Sprint 005 behavior:
- Budgets are managed through `GET /api/v1/budgets`, `POST /api/v1/budgets`, and `GET /api/v1/budgets/status`.
- `period` accepts `monthly` and `yearly`.
- `amount_usd` must be greater than `0`.
- `alert_at_pct` must be between `1` and `100`.
- Budget creation validates that `project_id` references an existing project.
- The API treats `project_id` plus `period` as unique in the service layer: posting the same pair updates the existing budget instead of creating a duplicate.

Relationship to usage:
- Budget status is calculated from `SUM(ai_requests.estimated_cost)` for the same project.
- Monthly budgets use current-month `ai_requests.created_at` records.
- Yearly budgets use current-year `ai_requests.created_at` records.
- `consumed_pct` is calculated as `spent_usd / amount_usd * 100`.
- Status is `ok`, `warning`, or `exceeded`.

## Sprint 002 Limitations

- No production authentication or authorization is implemented.
- There is no user-project membership table; `projects.owner_id` is the only current user association.
- Duplicate project validation is scoped to `name` plus `org_id`.
- AI request metering tables exist, but provider calls and token metering behavior are out of scope.

## Sprint 003 Limitations

- AI request records are manual/internal metering events only.
- No external provider calls, proxy behavior, streaming, or provider API keys are implemented.
- No budget enforcement, alerts, rate limiting, or analytics endpoints are implemented.
- `estimated_cost` is accepted from the request and not independently calculated yet.
- `status` is validated as non-empty text, but no enum is enforced yet.

## Sprint 004 Usage Aggregation

- `ai_requests` is the source of truth for usage query endpoints.
- No new tables or columns were added for usage aggregation.
- Aggregations are computed at query time.
- Grouping is available by project, user, and provider/model.
- Optional filters use existing `ai_requests` columns: `created_at`, `provider`, `model`, `status`, `project_id`, and `user_id`.

Sprint 004 limitations:
- No budget enforcement or budget status calculation.
- No alerts, forecasting, recommendations, dashboard, frontend, or provider calls.
- Aggregation is intentionally simple and unpaginated for the MVP backend.

## Sprint 005 Budget Limitations

- Budget records do not trigger notifications or alerts.
- Budget status does not block AI request recording or provider use.
- No billing, invoicing, payments, auth, dashboard, provider calls, or cloud infrastructure were added.
- There is no database-level uniqueness constraint for `project_id` plus `period`; Sprint 005 enforces upsert behavior in the service layer to avoid a migration.
- Historical budget windows are not configurable yet; Sprint 005 uses current month and current year only.
