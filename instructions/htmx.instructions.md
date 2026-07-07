---
description: 'htmx conventions — hypermedia-driven UI, partial rendering, out-of-band swaps, and server-side patterns.'
applyTo: '**/*.html, **/*.htm'
---

# htmx Instructions

You are an expert engineer building hypermedia-driven UIs with htmx.

## Core Model

- **MUST**: treat the server as the source of truth for UI state and return HTML fragments, not JSON — htmx's model is "hypermedia as the engine of application state" (HATEOAS in practice); reintroducing a client-side JSON+templating layer defeats the point of using it.
- **MUST**: design endpoints to return the exact HTML fragment the triggering element needs (`hx-target`/`hx-swap` destination), not a full-page response — a full-page response swapped into a fragment target duplicates `<html>`/`<head>` into the DOM.
- **SHOULD**: name partial-returning endpoints distinctly from full-page endpoints (e.g. `/partials/todo-item/:id` vs `/todos/:id`) so it's clear from the route which shape a handler returns.

## Attributes & Interactions

- **SHOULD**: prefer `hx-trigger` modifiers (`changed`, `delay:500ms`, `throttle:1s`) over hand-written debounce/throttle JavaScript for common patterns like live search.
- **MUST**: use `hx-swap` deliberately (`innerHTML`, `outerHTML`, `beforeend`, etc.) — the default (`innerHTML`) silently discards event listeners attached to the target's children; pick `outerHTML` when you need to replace an element's own attributes too.
- **SHOULD**: use `hx-indicator` to show a loading state for any request that isn't near-instant — htmx doesn't show one by default, and a silent multi-hundred-ms request reads as a broken UI.

## Out-of-Band Swaps & Multi-Target Updates

- **SHOULD**: use `hx-swap-oob` when a single server response needs to update multiple, non-nested regions of the page (e.g. updating a cart icon badge alongside the main content swap) — this avoids a second round-trip just to sync a sibling widget.
- **MUST**: keep OOB swap targets' IDs stable and unique in the DOM — htmx matches OOB fragments by ID, and a duplicate ID causes silent, unpredictable swap behavior.

## Forms & Validation

- **MUST**: return the form fragment with inline validation errors (422/400 status + re-rendered form partial with error messages) on validation failure — don't return a bare error string that leaves the user's form state discarded.
- **SHOULD**: use `hx-boost` on regular links/forms in content-heavy pages to get SPA-like navigation without abandoning progressive enhancement — the plain HTML must still work if JS fails to load.

## Security

- **MUST**: apply the same server-side authorization/CSRF checks to htmx-triggered endpoints as to regular form submissions — htmx requests are still just HTTP requests and must not bypass your normal auth middleware.
- **MUST**: escape/sanitize any user-generated content injected into returned fragments — htmx swaps raw HTML into the DOM, so an unescaped fragment is a direct XSS vector, arguably more directly than a client-rendered template that escapes by default.

## Progressive Enhancement & Accessibility

- **SHOULD**: ensure interactive elements remain real, keyboard-accessible HTML controls (`<button>`, `<a href>`) with htmx attributes layered on — not `<div hx-get="...">` acting as a fake button with no keyboard/focus semantics.
- **MUST**: manage focus after a swap for significant content changes (e.g. move focus to a newly revealed form or error message) — htmx doesn't manage focus for you, and a silent DOM swap can strand screen-reader/keyboard users.

## Testing

- **SHOULD**: test server endpoints by asserting on the returned HTML fragment's structure (presence of expected elements/attributes), the same way you'd assert on a JSON shape for an API — treat the fragment as the contract.
- **MUST**: cover the "JS disabled" / plain-HTML-form-submit fallback path in at least one end-to-end test if the feature is meant to progressively enhance a working plain form.
