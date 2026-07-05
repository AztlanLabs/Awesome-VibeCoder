# Error Boundaries

Wrap a tree in a class-based `ErrorBoundary` that catches render-time errors, shows a recoverable fallback keyed by a `resetKey`, forwards the error to an injected reporting hook, and composes cleanly with `<Suspense>`.

> **Runnable example:** [recipe/error-boundaries.tsx](recipe/error-boundaries.tsx)
>
> ```bash
> cd recipe && npm install
> npx tsx error-boundaries.tsx
> # or: npm run error-boundaries
> ```

## Example scenario

A widget fetches user data and a child throws if the data is malformed. You want to: render a friendly fallback, log the error to your telemetry, and let the user reset the boundary to retry.

## The boundary

```tsx
class ErrorBoundary extends Component<Props, State> {
  state = { error: null as Error | null };

  static getDerivedStateFromError(error: unknown): State {
    return { error: error as Error };
  }

  componentDidCatch(error: Error, info: { componentStack: string }) {
    this.props.onError?.(error, info);
  }

  reset = () => this.setState({ error: null });

  componentDidUpdate(prev: Props) {
    if (this.state.error && this.props.resetKey !== prev.resetKey) {
      this.reset();
    }
  }

  render() {
    if (this.state.error) return this.props.fallback(this.state.error, this.reset);
    return this.props.children;
  }
}
```

## Reset by key

Bumping `resetKey` (e.g., the active record id) programmatically clears the fallback — great for "switch profile to retry" patterns.

```tsx
<ErrorBoundary resetKey={activeId} fallback={...}>
  <Widget id={activeId} />
</ErrorBoundary>
```

## Reporting hook

```tsx
function useErrorReporter() {
  return (error: Error, info: { componentStack: string }) => {
    console.error("[telemetry]", error.message, info.componentStack);
  };
}
```

## Composed with Suspense

Errors caught here and thrown promises caught by Suspense form a complete UI lifecycle: loading → success | error.

```tsx
<ErrorBoundary onError={report} fallback={(e, reset) => <Fallback e={e} reset={reset} />}>
  <Suspense fallback={<p>Loading…</p>}>
    <Widget id={activeId} />
  </Suspense>
</ErrorBoundary>
```

## Best practices

1. **Place boundaries near the crashing subtree**, not at the root, so unrelated UI stays interactive.
2. **Forward errors via `onError`** to telemetry; do not swallow them silently.
3. **Use a meaningful `resetKey`** tied to the data that caused the failure.
4. **Render a recoverable fallback** — include a Retry button that calls `reset()` or changes the `resetKey`.
5. **Combine with Suspense** to cover the full lifecycle: pending → data | error.