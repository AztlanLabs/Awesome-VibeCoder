---
description: 'Nuxt 4 conventions — file-based routing, data fetching (useFetch/useAsyncData), server routes (Nitro), and SSR/hydration patterns.'
applyTo: '**/*.vue, **/*.ts, **/*.js'
---

# Nuxt Instructions

You are an expert frontend engineer building full-stack applications with Nuxt (Vue's meta-framework).

## Data Fetching

- **MUST**: use `useFetch`/`useAsyncData` for data needed during SSR — a plain `fetch()`/`axios` call inside `onMounted` only runs client-side, causing a loading flash and losing SSR's SEO/perceived-performance benefit.
- **MUST**: give `useAsyncData` calls a stable, unique key when the URL alone doesn't disambiguate them (e.g. same endpoint called with different reactive params) — a colliding key causes Nuxt to reuse cached data across genuinely different requests.
- **SHOULD**: use `useFetch`'s reactive URL/params support (pass a ref or getter) instead of manually re-calling fetch in a `watch` — this keeps caching and dedup behavior intact.

## Rendering Modes

- **MUST**: pick the rendering mode deliberately per route (`ssr: true` default, `routeRules` for hybrid rendering, or `ssr: false` for SPA-only sections) rather than assuming one mode fits the whole app — a marketing page and an authenticated dashboard usually want different modes.
- **SHOULD**: use Nuxt's hybrid rendering (`routeRules` in `nuxt.config.ts`) to statically prerender content-only routes and SSR/CSR the dynamic ones, instead of forcing the entire app into one strategy.

## Server Routes (Nitro)

- **MUST**: put server-only logic (DB access, secrets, third-party API keys) in `server/api/*.ts` (Nitro routes) — never in a `.vue`/composable that ships to the client bundle.
- **SHOULD**: use Nitro's built-in caching (`defineCachedEventHandler`) for expensive, cacheable server routes instead of hand-rolling a cache layer.
- **MUST**: validate input in server routes (`readValidatedBody`, or a schema library) — server routes are a real backend surface, not a trusted internal boundary.

## Hydration & State

- **MUST**: avoid rendering non-deterministic values (random IDs, `Date.now()`, `window`-dependent values) directly in template output that's part of SSR — mismatches between server-rendered and client-hydrated markup cause hydration errors.
- **SHOULD**: use `useState` (Nuxt's SSR-safe state helper) for state that must be shared between server render and client hydration — a plain module-level `ref` is **not** request-scoped and will leak between concurrent SSR requests.
- **MUST**: gate genuinely client-only code (`window`, `localStorage`, browser-only libraries) behind `<ClientOnly>` or `import.meta.client` checks, not a bare top-level reference that will throw during SSR.

## Components & Composables

- **SHOULD**: extract reusable reactive logic into composables (`composables/useX.ts`, auto-imported) rather than duplicating `ref`/`computed` logic across components.
- **MUST**: prefix composables with `use` so Nuxt's auto-import and tooling can distinguish them from plain utility functions.

## Performance

- **SHOULD**: use `<NuxtImg>`/`<NuxtPicture>` (Nuxt Image) for responsive, optimized images instead of raw `<img>` tags in production code.
- **MUST**: lazy-load below-the-fold, non-critical components with `defineAsyncComponent`/dynamic imports rather than including them in the critical initial bundle.

## Testing

- **MUST**: test server routes (`server/api/`) as plain handler functions with a mocked event, independent of a full app render.
- **SHOULD**: use `@nuxt/test-utils` for component/integration tests that need the Nuxt runtime context (auto-imports, `useFetch`, etc.) rather than a bare Vue Test Utils setup that won't resolve Nuxt-specific composables.
