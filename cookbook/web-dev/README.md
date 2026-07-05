# Web Development Cookbook

Production recipes for the modern web stack — Node.js, React, Next.js, Astro, Svelte, and Vue. Each recipe ships a focused markdown guide **and** a runnable `.ts`/`.tsx` example.

These recipes are pure framework idioms — they do **not** require the GitHub Copilot SDK.

## Sections

| Framework | Focus |
| --- | --- |
| [Node.js](nodejs/) | Streaming, graceful shutdown, structured logging, worker pools, rate limiting |
| [React 19](react/) | `use()`/Suspense, form actions, optimistic updates, compound components, error boundaries |
| [Next.js 16](nextjs/) | Server Actions, middleware auth, streaming SSR, streaming route handlers, on-demand ISR |
| [Astro 5](astro/) | Content collections, islands hydration strategy |
| [Svelte 5](svelte/) | Runes reactivity, transitions & actions |
| [Vue 3](vue/) | Composables + Pinia, SFC `<script setup>` |

## Running a Recipe

Each framework folder has a `recipe/` directory with a `package.json` and example files.

```bash
cd web-dev/nodejs/recipe
npm install
npx tsx streaming-responses.ts
```

See each framework's `README.md` and `recipe/README.md` for full command lists.

## Contributing

Add a recipe by dropping a markdown file in the relevant framework folder and a matching example under `recipe/`. Follow the conventions in [Copilot SDK cookbook recipes](../copilot-sdk/) and the repository's [CONTRIBUTING.md](../../CONTRIBUTING.md).