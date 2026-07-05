# Runnable Recipe Examples — Next.js (App Router)

This folder contains standalone, executable TypeScript examples for each Next.js cookbook recipe. Each file can be run directly with `tsx` or via the npm scripts defined in `package.json`.

## Prerequisites

- Node.js 20 or later
- Install dependencies once:

```bash
npm install
```

## Running Examples

### Using npm scripts

```bash
npm run <script-name>
```

### Using tsx directly

```bash
npx tsx <filename>
```

## Available Recipes

| Recipe                          | npm script                              | Direct command                                | Description                                                              |
| ------------------------------- | --------------------------------------- | --------------------------------------------- | ------------------------------------------------------------------------ |
| Server Actions Validation        | `npm run server-actions-validation`    | `npx tsx server-actions-validation.tsx`       | Server Action with hand-rolled Zod-style validation + `useActionState`   |
| Middleware Auth                  | `npm run middleware-auth`               | `npx tsx middleware-auth.ts`                   | `middleware.ts` JWT/cookie check with matcher + in-memory verifier demo  |
| Streaming SSR                   | `npm run streaming-ssr`                 | `npx tsx streaming-ssr.tsx`                   | `Suspense` + `loading.tsx` patterns with a simulated slow fetcher        |
| Route Handlers Streaming         | `npm run route-handlers-streaming`     | `npx tsx route-handlers-streaming.ts`         | `route.ts` returning a `ReadableStream` `Response` (SSE), backpressure    |
| ISR On-Demand                    | `npm run isr-on-demand`                 | `npx tsx isr-on-demand.ts`                    | Tag-based in-memory cache simulating `revalidatePath`/`revalidateTag`    |

> **Note:** Some of these examples simulate Next.js framework internals (Server Actions transport, RSC stream, Route Handler runtime, ISR cache) in plain TypeScript so they can be executed with `tsx` without scaffolding a full app. To use the patterns in a real project, run `npx create-next-app@latest` and paste the snippets into the appropriate `app/` files.

## Parent Cookbook

See [the parent cookbook README](../README.md) for context and the full recipe list.