---
description: 'Flask conventions for lightweight Python web apps and APIs — blueprints, application factories, and extension usage.'
applyTo: '**/*.py'
---

# Flask Instructions

You are an expert Python engineer building web applications and APIs with Flask.

## Application Structure

- **MUST**: use the application factory pattern (`create_app()`) rather than a module-level `app = Flask(__name__)` — a global app instance makes testing with different configs (and multiple app instances) impossible.
- **MUST**: organize routes with `Blueprint` per resource/domain, registered in the factory — don't accumulate every route in one file as the app grows.
- **SHOULD**: keep configuration in a `Config` class hierarchy (`Config` → `DevConfig`/`ProdConfig`/`TestConfig`) loaded via `app.config.from_object()`, not scattered `os.environ.get()` calls through the codebase.

## Request Handling & Validation

- **MUST**: validate request bodies/query params with a schema library (Pydantic, Marshmallow) — never trust `request.json`/`request.args` directly into business logic or a DB write.
- **MUST**: return a consistent JSON error shape (`{"error": {"code": ..., "message": ...}}`) via a registered `errorhandler`, not ad-hoc `return {"error": str(e)}, 500` scattered across routes.
- **SHOULD**: use `flask.g` for per-request context (current user, DB session) rather than thread-locals you manage yourself.

## Database Access

- **SHOULD**: use Flask-SQLAlchemy (or SQLAlchemy directly) with a session scoped to the request lifecycle (teardown via `app.teardown_appcontext`), so connections are always released even on error.
- **MUST**: wrap multi-step writes in an explicit transaction (`session.begin()` / `with db.session.begin():`) — don't rely on autocommit for anything that needs all-or-nothing semantics.
- **MUST**: use parameterized queries (the ORM, or `text()` with bound params) — never format user input directly into a SQL string.

## Blocking I/O & Concurrency

- **MUST**: know that Flask's default dev server and most sync WSGI deployments (gunicorn sync workers) block per-request on I/O — a slow external call ties up a whole worker. Use `gunicorn` with enough workers/threads, or move to an async framework, if throughput matters.
- **SHOULD**: offload slow, non-request-critical work (emails, thumbnailing) to a task queue (Celery/RQ) rather than doing it inline in the request/response cycle.

## Security Defaults

- **MUST**: enable CSRF protection (Flask-WTF / Flask-SeaSurf) for any form-based, cookie-authenticated endpoint — API-only JSON endpoints using token auth are the exception, not the default.
- **MUST**: set `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, and `SESSION_COOKIE_SAMESITE` explicitly in production config — Flask's defaults are permissive for local development, not production.
- **SHOULD NOT**: run with `debug=True` in production — the Werkzeug debugger's interactive console is a remote code execution vector if reachable.

## Testing

- **MUST**: test via Flask's `test_client()` against the app created by the factory with a `TestConfig` — never test against a running dev server.
- **SHOULD**: use `pytest` fixtures to build a fresh app/client per test (or per module, with DB rollback) rather than sharing global state across tests.

## Extensions

- **SHOULD**: initialize extensions (SQLAlchemy, Migrate, Login) with the `init_app(app)` pattern inside the factory, not bound to a module-level `app` — this is what makes the factory pattern actually composable.
