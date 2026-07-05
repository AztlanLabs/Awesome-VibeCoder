# Web Development Cookbook — Next.js

Short, practical recipes for building Next.js 16 (App Router) applications. Each recipe is concise, copy-pasteable, and points to a standalone runnable example.

These recipes are aligned with the conventions described in [`instructions/nextjs.instructions.md`](../../../instructions/nextjs.instructions.md).

## Recipes

- [Server Actions Validation](server-actions-validation.md): Server Action with hand-rolled Zod-style schema validation, typed `prevState`, `useActionState`, progressive enhancement.
- [Middleware Auth](middleware-auth.md): `middleware.ts` protecting routes via JWT/cookie check, redirects, URL rewriting, and `matcher` config.
- [Streaming SSR](streaming-ssr.md): Streaming Server Components with `Suspense` boundaries, `loading.tsx` patterns, simulated slow fetch, partial HTML flush.
- [Route Handlers Streaming](route-handlers-streaming.md): `app/api/.../route.ts` returning a `ReadableStream` body (SSE/NDJSON) with backpressure and `AbortController` on disconnect.
- [ISR On-Demand](isr-on-demand.md): On-demand revalidation via `revalidatePath`/`revalidateTag` from a Route Handler and a Server Action, plus `next: { revalidate }` and `generateStaticParams`.

## Running Examples

Each recipe has a standalone, executable TypeScript snippet under [`recipe/`](recipe/). Install once, then run any example:

```bash
cd recipe && npm install
npx tsx <example-file>
# or
npm run <script-name>
```

See [`recipe/README.md`](recipe/README.md) for the full table of scripts and direct commands.

## Notes

- These recipes target **Next.js 16 App Router** idioms: Server Components by default, `'use client'` for interactivity, **Server Actions**, `route.ts` Route Handlers, `middleware.ts`, Streaming, and ISR via `revalidate`/`revalidateTag`.
- **Never use `next/dynamic` with `{ ssr: false }` inside a Server Component.** Move client-only UI into a dedicated Client Component and import it directly. See [Server Actions Validation](server-actions-validation.md) and [Streaming SSR](streaming-ssr.md) for the correct pattern.
- In Next.js 16, async request APIs (`cookies()`, `headers()`, `draftMode()`, `params`, `searchParams`) are **async** — await them.
- The runnable snippets are standalone: they simulate framework internals (Server Action transport, RSC stream, Route Handler runtime, ISR cache) in plain TS so they execute with `tsx`. **Full app scaffolding requires `npx create-next-app@latest`.**
- Code is type-safe, uses no `any`, and avoids unnecessary dependencies (validation is hand-rolled so no `zod` install is required for the recipe).

## Contributing

Follow repository guidance in [CONTRIBUTING.md](../../../CONTRIBUTING.md).