# Runnable Recipe Examples — Svelte

Minimal example files for each Svelte 5 cookbook recipe. The `.svelte.ts` runes module can be type-checked directly; the `.svelte` component requires the Svelte compiler (run through Vite) to render and exercise transitions in the DOM.

## Prerequisites

- Node.js 18 or later
- The Svelte CLI for full execution:

```bash
npm create svelte@latest
```

## How to use these files

| Recipe               | File                                     | How to run                                                                                  |
| -------------------- | ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| Stores & Reactivity  | `stores-reactivity.svelte.ts`            | Type-check with `npx tsc --noEmit` (the Svelte language plugin compiles runes). To execute, import `demonstrate()` from a SvelteKit/Vite app — runes run inside the Svelte compiler's reactive transform. |
| Transitions & Actions | `transitions-actions.svelte`            | Drop into a SvelteKit/Vite project (e.g. `src/routes/+page.svelte`) and run `npm run dev`. Actions and transitions need the Svelte compiler + a DOM. |

## Type-checking the runes module

```bash
npm install
npx tsc --noEmit
```

For end-to-end render/transition inspection, use SvelteKit:

```bash
npm create svelte@latest my-app
cd my-app
npm install
npm run dev
```

…then import `createCounter` / the `transitions-actions.svelte` component into a route.

## Parent Cookbook

See the [parent cookbook README](../README.md).