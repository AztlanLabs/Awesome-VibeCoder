---
description: 'Axum web framework conventions for Rust — routing, extractors, middleware, SSE/streaming, and error handling.'
applyTo: '**/*.rs'
---

# Rust Axum Instructions

You are an expert Rust engineer building web services with Axum and Tokio.

## Routing & Handlers

- **MUST**: compose routes with `Router::new().route(...).nest(...)` per module/domain, merged in `main` — avoid one giant flat route list.
- **MUST**: use typed extractors (`Path<T>`, `Query<T>`, `Json<T>`, `State<T>`) for handler inputs — never manually parse the raw `Request` body/URI when a built-in extractor covers the case.
- **SHOULD**: define request/response DTOs with `serde::{Serialize, Deserialize}` and validate them (via `validator` or manual checks) before touching domain logic — don't let malformed JSON reach business code.

## State & Dependency Injection

- **MUST**: share application state (DB pool, config, clients) via `State<Arc<AppState>>`, not global `static`/`lazy_static` — this keeps state testable and avoids hidden global mutation.
- **SHOULD**: keep `AppState` cheap to clone (wrap heavy resources in `Arc`) since Axum clones state per request.

## Error Handling

- **MUST**: implement `IntoResponse` for your domain error type so handlers can return `Result<T, AppError>` directly — don't `.unwrap()`/`.expect()` inside a handler; a panic there is a 500 with no control over the response shape.
- **MUST**: map errors to a stable JSON error envelope (`{"code": ..., "message": ...}`) with the correct status code in one central `IntoResponse` impl, not duplicated per handler.
- **SHOULD**: use `anyhow`/`thiserror` internally and convert to `AppError` at the handler boundary, keeping the internal error types rich and the external contract stable.

## Middleware & Extractors

- **SHOULD**: implement cross-cutting concerns (auth, request-id, tracing span, rate limiting) as `tower::Layer`/middleware rather than repeating logic at the top of every handler.
- **MUST**: validate auth via an extractor (`FromRequestParts`) that fails the request before the handler body runs — don't check auth manually inside each handler.
- **SHOULD**: use `tower_http` layers (`TraceLayer`, `CorsLayer`, `CompressionLayer`, `TimeoutLayer`) instead of hand-rolling these concerns.

## Streaming & SSE

- **MUST**: bound any streaming response (SSE, chunked) with a way for the client disconnect to cancel the underlying task — an axum `Sse` stream tied to a `tokio::sync::mpsc` channel should stop producing when the receiver drops.
- **SHOULD**: apply backpressure on SSE/streaming channels with a bounded channel (`mpsc::channel(N)`), not an unbounded one — an unbounded channel behind a slow client is an unbounded memory leak.
- **MUST**: send periodic keep-alive/comment events on long-lived SSE connections so intermediate proxies don't time out the connection.

## Async & Concurrency

- **MUST**: never block the async runtime with synchronous I/O or CPU-heavy work inside a handler — use `tokio::task::spawn_blocking` for blocking calls (sync DB drivers, file I/O, heavy computation).
- **SHOULD**: use `tokio::select!` with a cancellation token (`tokio_util::sync::CancellationToken`) for long-running background tasks so they shut down cleanly on server shutdown.

## Testing

- **MUST**: test handlers with `axum::body::Body` + `tower::ServiceExt::oneshot` against the built `Router` — this exercises the full middleware stack without binding a real socket.
- **SHOULD**: use `sqlx::test` (or a test-scoped transaction) for DB-touching integration tests so each test runs isolated and rolls back automatically.
