# Web Development Cookbook — React

Short, practical recipes for **React 19 + TypeScript** patterns: data fetching with Suspense and `use()`, form actions with `useActionState` / `useFormStatus`, optimistic UI, accessible compound components, and resilient error boundaries. These are pure React patterns (no Next.js required) and run with a minimal Vite-like setup.

Each recipe is concise, copy-pasteable, and links to a runnable `.tsx` example in [`recipe/`](recipe/).

## Recipes

- [Data Fetching with Suspense & `use()`](data-fetching-suspense.md): Promise-based data fetching with a tiny client cache and `ErrorBoundary`.
- [Form Actions](form-actions.md): `useActionState` + `useFormStatus` with an async, validating action and progressive enhancement.
- [Optimistic Updates](optimistic-updates.md): `useOptimistic` + `useTransition` for a todo list with simulated network latency.
- [Compound Components](compound-components.md): Accessible Tabs (TabList / Tab / TabPanel) with shared context and keyboard navigation.
- [Error Boundaries](error-boundaries.md): Class-based `ErrorBoundary` with fallback UI, reset key, and an error reporting hook, composed with `Suspense`.

## Running Examples

Each recipe ships a standalone `.tsx` file under `recipe/`. From any recipe folder:

```bash
cd recipe && npm install
npx tsx <recipe-id>.tsx          # e.g. npx tsx form-actions.tsx
# or: npm run <recipe-id>        # e.g. npm run form-actions
```

The examples mount to the DOM via `react-dom/client` `createRoot` when a browser `document` is present. When run headlessly under `tsx`, they safely skip the DOM mount and print a textual description of what they would render.

## Contributing

Add a new recipe by creating a markdown file in this folder, a matching `.tsx` in `recipe/`, and a new script entry in `recipe/package.json`. Follow repository guidance in [CONTRIBUTING.md](../../../CONTRIBUTING.md).