---
description: 'SolidJS conventions — fine-grained reactivity, signals, stores, and SolidStart patterns.'
applyTo: '**/*.tsx, **/*.ts, **/*.jsx, **/*.js'
---

# SolidJS Instructions

You are an expert frontend engineer building applications with SolidJS.

## Reactivity Model

- **MUST**: remember Solid components run **once** — a component function body is setup code, not a render function that re-runs on every state change (unlike React). Do not write logic that assumes re-execution on each update.
- **MUST**: keep signal reads inside a reactive scope (JSX, `createEffect`, `createMemo`) if you want them tracked — destructuring a signal's value outside of one (`const { value } = mySignal()`) at component setup time captures a snapshot, not a reactive binding.
- **SHOULD**: use `createSignal` for atomic pieces of state and `createStore` for nested/object state you'll update at a sub-property path — a store gives you fine-grained updates (`setStore("user", "name", ...)`) without re-creating the whole object.

## Components & Props

- **MUST NOT**: destructure props (`const { name } = props`) at the top of a component — this breaks reactivity because it reads the value once instead of tracking the prop. Access via `props.name` inline, or wrap in `createMemo`/use `splitProps`/`mergeProps` helpers.
- **SHOULD**: use `<For>` (keyed) for list rendering instead of `Array.prototype.map` in JSX — `<For>` performs fine-grained per-item reconciliation instead of re-rendering the whole list on any change.
- **SHOULD**: use `<Show>`/`<Switch>`/`<Match>` for conditional rendering instead of ternaries/`&&` when the condition is a reactive signal — they avoid the JSX being re-evaluated unnecessarily.

## Effects & Derived State

- **MUST**: use `createMemo` for derived values read in multiple places, not a plain function call repeated in JSX — a plain function re-executes on every access; `createMemo` caches until a tracked dependency changes.
- **SHOULD**: keep `createEffect` for side effects only (DOM manipulation, logging, syncing to an external system) — don't use it to compute a value that another part of the UI needs; use `createMemo` for that.
- **MUST**: clean up subscriptions/timers/listeners created inside `createEffect` with `onCleanup` — Solid does not automatically dispose effect-created resources when the effect re-runs or the owner is disposed.

## Stores

- **SHOULD**: use `produce()` from `solid-js/store` for batched, mutation-style updates to a store within a single `setStore` call, rather than many sequential `setStore` calls.
- **MUST**: never mutate a store's underlying object directly (`store.user.name = "x"`) — always go through `setStore(...)`; direct mutation bypasses Solid's reactivity tracking.

## SolidStart (Meta-framework)

- **SHOULD**: use SolidStart's file-based routing and `routeData`/server functions for data loading rather than fetching in a `createEffect` on mount — server-loaded data avoids request waterfalls and works with SSR.
- **MUST**: mark server-only code with `"use server"` (server functions) so it's excluded from the client bundle — accidentally shipping server secrets/DB clients to the browser is a common SolidStart mistake.
- **SHOULD**: use SolidStart's built-in streaming SSR for slow data dependencies rather than blocking the full page render on every data source.

## Testing

- **SHOULD**: use `@solidjs/testing-library` (Testing-Library's Solid adapter) — it understands Solid's fine-grained updates and avoids the "act()"-style workarounds needed with less Solid-aware tooling.
- **MUST**: wrap signal updates in tests that need to observe reactive effects (e.g. `createEffect` results) appropriately — assertions immediately after a signal set may run before Solid's microtask-scheduled effect has flushed.
