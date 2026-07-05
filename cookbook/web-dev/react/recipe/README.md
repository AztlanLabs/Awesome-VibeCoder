# Runnable Recipe Examples — React

Standalone, executable TypeScript + React 19 examples for each React cookbook recipe.

## Prerequisites

- Node.js 18 or later
- Install dependencies:

```bash
npm install
```

## Running Examples

Each `.tsx` mounts a demo component via `react-dom/client` `createRoot` when run in a browser environment. Under headless `tsx`, the DOM mount is skipped and a textual description is logged instead.

```bash
npm run <recipe-id>
# or
npx tsx <recipe-id>.tsx
```

## Available Recipes

| Recipe               | npm script                    | Direct command                        | Description                                                      |
| -------------------- | ----------------------------- | ------------------------------------- | ---------------------------------------------------------------- |
| Data Fetching        | `npm run data-fetching-suspense` | `npx tsx data-fetching-suspense.tsx` | Suspense + `use()` promise cache with `ErrorBoundary`           |
| Form Actions         | `npm run form-actions`        | `npx tsx form-actions.tsx`            | `useActionState` + `useFormStatus` async action with validation  |
| Optimistic Updates   | `npm run optimistic-updates` | `npx tsx optimistic-updates.tsx`      | `useOptimistic` + `useTransition` todo list with latency         |
| Compound Components  | `npm run compound-components`| `npx tsx compound-components.tsx`     | Accessible Tabs context + keyboard nav                          |
| Error Boundaries     | `npm run error-boundaries`   | `npx tsx error-boundaries.tsx`       | Class `ErrorBoundary` + reset key + reporting hook              |

## Parent Cookbook

See the [parent cookbook README](../README.md).