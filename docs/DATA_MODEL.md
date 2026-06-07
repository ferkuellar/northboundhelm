# Data Model

Sprint 002 keeps the Sprint 001 schema unchanged.

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
- `provider`
- `model`
- `prompt_tokens`
- `completion_tokens`
- `total_tokens`
- `estimated_cost`
- `latency_ms`
- `status`
- `metadata` JSONB in PostgreSQL
- `created_at`

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

## Sprint 002 Limitations

- No production authentication or authorization is implemented.
- There is no user-project membership table; `projects.owner_id` is the only current user association.
- Duplicate project validation is scoped to `name` plus `org_id`.
- AI request metering tables exist, but provider calls and token metering behavior are out of scope.
