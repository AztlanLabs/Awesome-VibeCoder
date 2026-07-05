# Data Fetching with Suspense & `use()`

Fetch promise-based data declaratively with React 19's `use()` hook, suspending the tree while loading and recovering from failures via an `ErrorBoundary`.

> **Runnable example:** [recipe/data-fetching-suspense.tsx](recipe/data-fetching-suspense.tsx)
>
> ```bash
> cd recipe && npm install
> npx tsx data-fetching-suspense.tsx
> # or: npm run data-fetching-suspense
> ```

## Example scenario

You have an async API returning a JSON payload and want to render a stable view: a spinner while loading, the data on success, and a retry screen on error — without hand-rolled `isPending` / `error` state in every component.

## A tiny promise cache

React's `use()` unwraps a *promise*; passing the same promise instance across renders causes only one suspend. A naive module-level cache dedupes in-flight requests per key.

```tsx
type Cache = Map<string, Promise<unknown>>;
const cache: Cache = new Map();

function fetchProfile(id: string): Promise<{ id: string; name: string }> {
  let p = cache.get(id);
  if (!p) {
    p = fakeApi(id);
    cache.set(id, p);
    p.finally(() => cache.delete(id));
  }
  return p as Promise<{ id: string; name: string }>;
}
```

## Reading the promise with `use()`

```tsx
function Profile({ id }: { id: string }) {
  const profile = use(fetchProfile(id));
  return <p>Loaded {profile.name} ({profile.id})</p>;
}
```

## ErrorBoundary

`use()` rejects the suspense boundary on failure. A class boundary turns that into a recoverable fallback.

```tsx
class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };
  static getDerivedStateFromError(error: unknown): State {
    return { error: error as Error };
  }
  render() {
    if (this.state.error) {
      return <Fallback retry={() => this.setState({ error: null })} />;
    }
    return this.props.children;
  }
}
```

## Wiring it together

```tsx
<ErrorBoundary>
  <Suspense fallback={<p>Loading…</p>}>
    <Profile id="u_42" />
  </Suspense>
</ErrorBoundary>
```

## Best practices

1. **Cache the promise, not the value.** `use()` only suspends once per promise identity, so dedupe at the fetch boundary.
2. **Always pair `use()` with an `ErrorBoundary`.** Rejected promises crash the tree otherwise.
3. **Reset boundaries via a `key`** if you want a fresh fetch after an error.
4. **Avoid `use()` in loops / conditionals below the call.** Call it at the top of the component, like other hooks.
5. **Prefer Server Components or route-level suspense** for the initial render and `use()` for client-side navigations.