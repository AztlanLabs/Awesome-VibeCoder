# Islands Architecture

Ship zero JS by default and hydrate only the components that need interactivity. Astro's `client:` directives control when (and whether) a component island boots on the client.

> **Runnable example:** [recipe/islands-architecture.astro](recipe/islands-architecture.astro)
>
> ```bash
> # see recipe README for setup
> ```

## Example scenario

A mostly-static marketing page with a heavy interactive widget. You want HTML on first paint, then progressively hydrate components without blocking the main thread.

## Choosing a directive

| Directive            | When it hydrates                                  | Use when                                  |
| -------------------- | ------------------------------------------------- | ----------------------------------------- |
| `client:load`        | Immediately on page load                          | Critical, above-the-fold interactivity    |
| `client:idle`        | When the browser is idle (`requestIdleCallback`)  | Recommended default for most widgets       |
| `client:visible`     | When it scrolls into view (`IntersectionObserver`) | Below-the-fold or expensive widgets        |
| `client:only`        | Never on the server; only hydrates on the client  | Components that touch browser-only APIs     |
| (no directive)       | Never — server-rendered HTML only                 | Pure presentational components             |

## Composing islands

```astro
---
import Header from '../components/Header.astro';
import Search from '../components/Search.svelte';
import Comments from '../components/Comments.vue';
import Chart from '../components/Chart.jsx';

const greeting = 'Welcome';
---

<Header />
<Search client:load placeholder="Search docs" />
<Chart client:visible data={data} define:vars={{ theme: 'dark' }} />
<Comments client:only="vue" />
```

## Passing server values with `define:vars`

`define:vars` injects server-computed values as inline CSS custom properties scoped to the element, avoiding serialization to global scope.

```astro
<div define:vars={{ accent: colorPalette.accent }}>
  <Widget client:visible />
</div>
```

## Best practices

1. **Default to `client:idle`** for most islands; reach for `client:load` only when interactivity is on the critical path.
2. **Use `client:visible`** for below-the-fold islands to defer hydration cost entirely.
3. **Reserve `client:only`** for components that genuinely cannot render on the server (browser-only APIs, WebGL, etc.) — you lose SSR HTML and SEO.
4. **Keep islands small.** Split a big interactive component into a server-rendered shell + a tiny hydrated island.
5. **Prefer `define:vars` over inline `<script>`** for passing server data to client styles; for component props, pass normally.
6. **Audit bundle size per island** with `astro build`'s output — each island is its own JS chunk.