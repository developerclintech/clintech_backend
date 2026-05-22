# Clinics API

Initial FastAPI backend scaffold for healthcare workflows. The structure separates routing, business logic, PostgreSQL persistence, AI integrations, and observability so each area can evolve independently.

## Structure

```text
app/
  api/              FastAPI routers and dependency wiring
  core/             Settings, logging, monitoring, shared infrastructure
  db/               Async SQLAlchemy session and Alembic metadata
  middleware/       Request context, trace IDs, request logging
  models/           SQLAlchemy ORM models
  repositories/     Database query layer
  schemas/          Pydantic request/response contracts
  services/         Business logic and AI orchestration
tests/              Lightweight application tests
alembic/            Database migration environment
```

## Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
docker compose up -d postgres
alembic upgrade head
uvicorn app.main:app --reload
```

Open:

- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `GET /metrics`

## Architecture Notes

- Routes stay thin and call services.
- Services own business rules, audit decisions, and cross-repository workflows.
- Repositories own database queries only.
- PostgreSQL is accessed asynchronously through SQLAlchemy and asyncpg.
- Alembic owns schema migrations; the initial migration creates patients, audit logs, and AI interaction tables.
- AI providers sit behind an interface so mock, OpenAI, Azure, or local model providers can be swapped without changing API routes.
- Structured JSON logging includes request IDs and avoids request/response body logging by default to reduce PHI exposure.
- Audit records capture actor, action, entity, trace ID, and metadata without storing clinical text.
- Prometheus metrics expose request counts and latency.

## Database

Local development uses the Postgres service in `docker-compose.yml`.

Default connection string:

```text
postgresql+asyncpg://clinics:clinics_dev_password@localhost:5432/clinics
```

For production, set `DATABASE_URL` from the deployment environment and keep credentials out of source control.

## Healthcare Logging Guidance

This scaffold is designed for traceability, not full regulatory compliance by itself. Before production, add authentication, authorization, encryption policy, retention policy, access logging, alerting, secrets management, and a formal PHI logging review.
