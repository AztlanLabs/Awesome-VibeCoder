# Optimistic Updates

Update the UI synchronously for instant feedback using `useOptimistic`, while the real mutation runs in a `useTransition` — and reconcile on success or roll back on failure.

> **Runnable example:** [recipe/optimistic-updates.tsx](recipe/optimistic-updates.tsx)
>
> ```bash
> cd recipe && npm install
> npx tsx optimistic-updates.tsx
> # or: npm run optimistic-updates
> ```

## Example scenario

A message list should show a new message the instant the user presses Enter, even though the server takes ~400ms to confirm. On failure the optimistic message is reverted with an inline error.

## The model

```tsx
type Message = { id: string; text: string; status: "pending" | "saved" | "error" };
type Optimistic = Message & { optimistic?: boolean };
```

## `useOptimistic`

The reducer function appends an optimistic item to the confirmed list.

```tsx
const [optimistic, addOptimistic] = useOptimistic<Message[], Optimistic>(
  messages,
  (state, msg) => [...state, { ...msg, status: "pending", optimistic: true }],
);
```

## Mutation inside `useTransition`

```tsx
const [isPending, startTransition] = useTransition();

function send(text: string) {
  startTransition(async () => {
    const tempId = crypto.randomUUID();
    addOptimistic({ id: tempId, text });
    try {
      const saved = await api.post(text);
      setMessages((m) => [...m, saved]);
    } catch (e) {
      console.error("revert", e);
    }
  });
}
```

## Why this works

- `addOptimistic` is a **Reducer Like** updater; React replays it against the latest confirmed state during renders triggered by `setMessages`.
- The transition marks the work as non-urgent, so typing stays snappy.
- On commit, the optimistic copy is discarded and replaced by the real `saved` item.

### Demo input

```tsx
<input
  value={text}
  onChange={(e) => setText(e.target.value)}
  onKeyDown={(e) => {
    if (e.key === "Enter" && text.trim() && !isPending) {
      send(text.trim());
      setText("");
    }
  }}
/>
```

## Best practices

1. **Tag optimistic items** so rendering can style them (italic, spinner, etc.).
2. **Keep the optimistic shape identical** to the confirmed shape so diffs don't flicker.
3. **Roll back on error** by simply not appending the confirmed item — React discards the optimistic copy automatically.
4. **Use `useTransition` for any state that triggers the optimistic flow** so it can be interrupted.
5. **Avoid `useOptimistic` for data that must be consistent** (e.g., account balances) — only for UI perceived-latency.