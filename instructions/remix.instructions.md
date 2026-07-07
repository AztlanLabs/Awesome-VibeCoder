---
description: 'Remix (React Router v7 framework mode) conventions — loaders/actions, nested routing, and progressive enhancement.'
applyTo: '**/*.tsx, **/*.ts, **/*.jsx, **/*.js'
---

# Remix Instructions

You are an expert frontend engineer building full-stack applications with Remix (React Router's framework mode).

## Data Loading

- **MUST**: fetch data in route `loader` functions, not in `useEffect` on mount — loaders run on the server (and can run in parallel across nested routes), eliminating client-side request waterfalls and loading spinners for initial data.
- **MUST**: type loader return values with `useLoaderData<typeof loader>()` so route components get compile-time-checked access to loader data — don't widen it to `any`.
- **SHOULD**: colocate a route's data requirements with the route file (`loader` in the same file as the component) rather than a separate data-fetching layer — this is what enables Remix's nested-route parallel loading.

## Mutations

- **MUST**: perform writes in `action` functions, invoked via `<Form>` (or `useFetcher`) — not via a client-side `fetch` POST followed by manual cache invalidation.
- **MUST**: return validation errors from the `action` as data (not a thrown exception) so the calling form can render field-level errors — reserve `throw` in actions/loaders for actual error responses (404, 500).
- **SHOULD**: use `useFetcher` for mutations that shouldn't trigger full navigation (e.g. a "like" button, inline edit) — reserve `<Form>` for mutations that should navigate afterward.

## Progressive Enhancement

- **MUST**: build forms with real `<Form method="post">` elements that work with JavaScript disabled — Remix's model assumes the server round-trip is the baseline, with client-side enhancement layered on top, not the other way around.
- **SHOULD NOT**: gate core functionality behind `useEffect`-driven client-only logic — if the feature can't work without JS, you've lost Remix's main architectural advantage.

## Routing & Layouts

- **MUST**: use nested routes (`app/routes/`) with `<Outlet />` for shared layouts — don't duplicate layout markup across sibling routes that share a shell.
- **SHOULD**: use resource routes (routes with no default export, only a `loader`/`action`) for non-HTML endpoints (webhooks, file downloads, API-style JSON) instead of standing up a separate API server.

## Error Handling

- **MUST**: export an `ErrorBoundary` per route (or rely on the root one deliberately) and throw `Response`s with proper status codes from loaders/actions (`throw new Response("Not Found", { status: 404 })`) rather than returning error state as normal data.
- **SHOULD**: distinguish expected errors (404, validation failure — return as data) from unexpected errors (thrown exceptions — caught by `ErrorBoundary`) rather than routing everything through one mechanism.

## Performance

- **SHOULD**: use `defer`/streaming for slow, non-critical data so the fast parts of a loader's response can render immediately while the slow part streams in via `<Suspense>` + `<Await>`.
- **MUST**: set appropriate `Cache-Control` headers from loaders (`headers()` export or response headers) for cacheable data — Remix does not cache loader responses for you by default.

## Testing

- **MUST**: test loaders/actions as plain functions (call them directly with a constructed `Request`/`params`) rather than only through full component render trees — this isolates data-layer bugs from UI bugs.
- **SHOULD**: use Playwright/end-to-end tests for the progressive-enhancement guarantee (form works with JS disabled) since unit tests can't verify that property.
