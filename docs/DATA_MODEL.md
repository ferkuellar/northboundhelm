# Data Model

Sprint 001 tables:

- `users`
- `projects`
- `ai_requests`
- `budgets`

`projects.owner_id`, `ai_requests.user_id`, `ai_requests.project_id`, and `budgets.project_id` use foreign keys. AI request metering queries are supported by composite indexes on project, user, provider/model, and status with `created_at`.

