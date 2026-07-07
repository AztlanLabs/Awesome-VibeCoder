---
description: 'FastAPI conventions for async Python APIs — dependency injection, Pydantic validation, and background tasks.'
applyTo: '**/*.py'
---

# FastAPI Instructions

You are an expert Python engineer building async APIs with FastAPI.

## Routing & Structure

- **MUST**: organize routes with `APIRouter` per resource/domain and mount them in the main app — don't accumulate every endpoint in one `main.py`.
- **SHOULD**: version routes at the router level (`APIRouter(prefix="/api/v1/orders")`) rather than sprinkling version strings through path decorators.
- **MUST**: declare explicit `response_model` (or return-type annotation) on every route — it drives OpenAPI generation, output filtering, and catches accidental field leaks (e.g. password hashes).

## Validation & Schemas

- **MUST**: use Pydantic models (v2) for request/response bodies — never accept raw `dict`/`Request.json()` and hand-validate.
- **SHOULD**: separate "Create"/"Update"/"Read" schemas per resource (`OrderCreate`, `OrderUpdate`, `OrderRead`) instead of one model with every field optional; this makes required-vs-optional explicit per operation.
- **MUST**: use `Field(...)` constraints (`min_length`, `ge`/`le`, `pattern`) for domain validation instead of re-validating manually in the route body.

## Dependency Injection

- **MUST**: use `Depends()` for cross-cutting concerns (DB session, current user, pagination params) — don't instantiate a DB session or re-parse auth headers inside every route function.
- **SHOULD**: scope database sessions per-request via a `yield`-based dependency so the session is guaranteed to close (and roll back on exception) even if the handler raises.
- **SHOULD**: use `Depends()` chains for authorization (`Depends(require_role("admin"))`) rather than an `if` check duplicated across handlers.

## Async & Concurrency

- **MUST**: use `async def` route handlers and `await` all I/O (DB, HTTP calls, file I/O) — a blocking synchronous call inside an `async def` route stalls the entire event loop, not just that request.
- **SHOULD**: if you must call blocking/synchronous code, offload it via `run_in_threadpool` (or make the route `def`, not `async def`, so FastAPI runs it in its threadpool automatically).
- **MUST**: use an async DB driver/ORM (SQLAlchemy 2.0 async, `asyncpg`) when the route is `async def` — mixing sync DB calls into async routes defeats the concurrency model.

## Errors & Responses

- **MUST**: raise `HTTPException` (or a custom exception + `exception_handler`) with a stable error shape (`{"code": ..., "message": ..., "details": ...}`) — never let an unhandled exception leak a stack trace to the client.
- **SHOULD**: register a global exception handler for domain exceptions so error-shape logic lives in one place, not duplicated per route.

## Background Work & Lifecycle

- **SHOULD**: use `BackgroundTasks` for fire-and-forget post-response work (sending an email, invalidating a cache); use a real task queue (Celery/Arq) for anything that must survive a process restart or needs retries.
- **MUST**: use the `lifespan` context manager (not deprecated `@app.on_event`) for startup/shutdown resource management (DB pool, HTTP client).

## Testing

- **MUST**: test routes with `httpx.AsyncClient` (or `TestClient`) against the ASGI app directly — not by spinning up a real server.
- **SHOULD**: override dependencies (`app.dependency_overrides`) to inject test doubles for the DB session and auth, rather than mocking internals.
