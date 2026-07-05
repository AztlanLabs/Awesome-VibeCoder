# Content Collections (Content Layer API)

Type-safe Markdown/MDX content in Astro 5 using the Content Layer API: define a `zod` schema in `src/content/config.ts`, render entries with `getCollection` / `getEntry`, and get inferred frontmatter types.

> **Runnable example:** [recipe/content-collections.ts](recipe/content-collections.ts)
>
> ```bash
> # see recipe README for setup
> ```

## Example scenario

You author docs as Markdown with frontmatter (`title`, `tags`, `draft`, `publishedAt`). You want compile-time validation of frontmatter, autocomplete in templates, and a way to query the collection — all without runtime surprises from malformed Markdown.

## Define a collection with `zod`

Astro 5's Content Layer API lives in `src/content/config.ts` (or `.js`). Use `defineCollection` with `loader` + `schema`.

```ts
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const docs = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/docs' }),
  schema: z.object({
    title: z.string(),
    tags: z.array(z.string()).default([]),
    draft: z.boolean().default(false),
    publishedAt: z.coerce.date(),
  }),
});

export const collections = { docs };
```

The `schema` is the single source of truth: frontmatter that does not match fails the build.

## Query with `getCollection` and `getEntry`

```ts
---
import { getCollection, getEntry } from 'astro:content';

const published = (await getCollection('docs', (entry) => !entry.data.draft))
  .sort((a, b) => b.data.publishedAt.getTime() - a.data.publishedAt.getTime());

const featured = await getEntry('docs', 'getting-started');
---
```

`entry.id` is the stable slug; `entry.data` is the parsed (typed) frontmatter; `entry.body` is raw Markdown; `render(entry)` gives you `<Content />`.

## Render an entry

```ts
---
import { getEntry, render } from 'astro:content';
const post = await getEntry('docs', 'getting-started');
const { Content } = await render(post);
---
<Content />
```

## Best practices

1. **Coerce dates** with `z.coerce.date()` so `2025-01-31` from YAML becomes a `Date`.
2. **Filter at the source** with the second arg to `getCollection` to skip drafts cheaply.
3. **Use `glob` loader** for filesystem Markdown; use the `fetch` / `file` loaders for remote or JSON content.
4. **One collection per content shape.** Don't overload a single schema with optional fields per entry type — split into multiple collections.
5. **Keep `config.ts` typed exports** so route files get inference for `collections` and `getEntry` lookups.