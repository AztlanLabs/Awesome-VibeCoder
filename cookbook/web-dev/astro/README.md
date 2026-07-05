# Web Development Cookbook — Astro

Short, practical recipes for **Astro 5 + TypeScript** patterns: type-safe Markdown content via the Content Layer API, and Islands architecture with client hydration directives. These recipes focus on framework idioms; running a full Astro app requires the official Astro CLI (`npm create astro@latest`).

Each recipe is concise, copy-pasteable, and links to a runnable example in [`recipe/`](recipe/).

## Recipes

- [Content Collections](content-collections.md): The Content Layer API with `src/content/config.ts`, `zod` schemas, `getCollection`/`getEntry`, and type-safe frontmatter.
- [Islands Architecture](islands-architecture.md): `client:load`, `client:idle`, `client:visible`, `client:only`, `define:vars`, and choosing a directive per component.

## Running Notes

Full Astro execution (rendering `.astro` files, Markdown collections, hydration) requires the Astro toolchain. Boot a project with:

```bash
npm create astro@latest
```

The runnable files in `recipe/` are minimal snippets that demonstrate the core APIs and can be type-checked inline or pasted into a fresh Astro project.

## Contributing

Add a new recipe by creating a markdown file in this folder and a matching file in `recipe/`. Follow repository guidance in [CONTRIBUTING.md](../../../CONTRIBUTING.md).