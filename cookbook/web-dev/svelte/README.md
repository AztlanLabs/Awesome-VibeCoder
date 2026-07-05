# Web Development Cookbook — Svelte

Short, practical recipes for **Svelte 5 + TypeScript** patterns: runes-based reactivity (`$state`, `$derived`, `$effect`, `$props`) in `.svelte.ts` modules, and composable transitions with Svelte Actions. These recipes focus on framework idioms; running a full Svelte app requires the official Svelte CLI (`npm create svelte@latest`).

Each recipe is concise, copy-pasteable, and links to a runnable example in [`recipe/`](recipe/).

## Recipes

- [Stores & Reactivity](stores-reactivity.md): Svelte 5 runes (`$state`, `$derived`, `$effect`, `$props`) vs classic stores, `.svelte.ts` modules, and passing reactive state.
- [Transitions & Actions](transitions-actions.md): `fade`, `slide`, `fly`, `crossfade`, custom `tick`/easing, and Svelte Actions via `use:`.

## Running Notes

Full Svelte execution (compiling `.svelte` components, transitions in the DOM) requires the Svelte compiler, typically through Vite. Boot a project with:

```bash
npm create svelte@latest
```

The runnable files in `recipe/` are minimal snippets demonstrating the core APIs. `.svelte.ts` modules can be type-checked directly; `.svelte` components need the Svelte compiler to run end-to-end (see [recipe/README.md](recipe/README.md) for compile steps).

## Contributing

Add a new recipe by creating a markdown file in this folder and a matching file in `recipe/`. Follow repository guidance in [CONTRIBUTING.md](../../../CONTRIBUTING.md).