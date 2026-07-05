# Runnable Recipe Examples — Astro

Minimal example files for each Astro cookbook recipe. These demonstrate the core Astro 5 APIs (Content Layer, islands directives) but are **not** runnable as standalone Node scripts — the `astro:content` and `astro/loaders` modules are virtual modules provided by the Astro toolchain.

## Prerequisites

- Node.js 18 or later
- The Astro CLI for full execution:

```bash
npm create astro@latest
```

## How to use these files

| Recipe              | File                                  | Where it goes / How to run                                                                 |
| ------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------ |
| Content Collections | `content-collections.ts`               | Paste into a fresh Astro project as `src/content/config.ts`, then call `getCollection`/`getEntry` from `.astro` routes. Type-check the schema with `astro check`. |
| Islands Architecture | `islands-architecture.astro`          | Drop into a fresh Astro project (e.g. `src/pages/`) and supply the imported components (`Header.astro`, `Search.svelte`, `Chart.jsx`, `Comments.vue`). Run `npm run dev`. |

## Type-checking the snippets

```bash
npm install
npx tsc --noEmit                # checks the .ts schema
npx astro check                 # checks .astro files (run inside an Astro project)
```

## Running a full app

Because Astro compiles `.astro` files and resolves the `astro:content` / `astro/loaders` virtual modules at build time, these snippets are designed to be copied into a CLI-booted project rather than executed directly. Start with:

```bash
npm create astro@latest my-app
cd my-app
npm install
```

Then paste the recipe content into the appropriate paths (`src/content/config.ts`, `src/pages/...`) and run `npm run dev`.

## Parent Cookbook

See the [parent cookbook README](../README.md).