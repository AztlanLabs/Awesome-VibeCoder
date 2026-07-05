# Stores & Reactivity (Svelte 5 Runes)

Svelte 5 replaces the classic `writable`/`readable` store API with **runes** (`$state`, `$derived`, `$effect`, `$props`) that work in both `.svelte` components and `.svelte.ts`/`.svelte.js` modules. This recipe shows rune-based reactive modules and how they relate to classic stores.

> **Runnable example:** [recipe/stores-reactivity.svelte.ts](recipe/stores-reactivity.svelte.ts)
>
> ```bash
> # see recipe README for setup
> ```

## Example scenario

You want a reactive counter module shared across components — incrementing it updates every consumer — but written with the new runes API and full type inference, no `subscribe` boilerplate.

## Runes in a `.svelte.ts` module

Runes work in non-component modules as long as the file extension is `.svelte.ts` (or `.svelte.js`). Export functions that close over `$state` so callers read reactive values via getters.

```ts
export function createCounter(initial = 0) {
  let count = $state(initial);
  let doubled = $derived(count * 2);
  return {
    get count() { return count; },
    get doubled() { return doubled; },
    increment() { count += 1; },
    decrement() { count -= 1; },
    reset() { count = 0; },
  };
}
```

Reading `counter.count` inside a component re-tracks; calling `counter.increment()` propagates.

## Effects with `$effect`

`$effect` runs after the DOM updates and re-runs when its reactive dependencies change. Use it for side effects (logging, subscriptions), not for deriving state.

```ts
$effect(() => {
  console.log('count is now', counter.count);
});
```

## Component props with `$props`

```svelte
<script lang="ts">
  let { initialValue = 0, label = 'Counter' }: { initialValue?: number; label?: string } = $props();
  const counter = createCounter(initialValue);
</script>

<button onclick={() => counter.increment()}>{label}: {counter.count} (x2 = {counter.doubled})</button>
```

## Runes vs classic stores

| Concern                | Classic store (`writable`)            | Runes (`$state`)                       |
| ---------------------- | ------------------------------------ | -------------------------------------- |
| Declaration            | `const n = writable(0)`              | `let n = $state(0)`                    |
| Read in component      | `{$n}` or `$n` (auto-subscription)   | `n.value` / getter                      |
| Update                 | `n.set(v)` / `n.update(v => v + 1)`  | `n = v` (or mutate object fields)       |
| Derived value          | `derived(n, $n => $n * 2)`           | `let d = $derived(n * 2)`              |
| Side effects           | `n.subscribe(v => ...)` (manual unsub) | `$effect(() => ...)` (auto-tracked)    |
| Outside a component     | Any `.ts` file                       | Must be `.svelte.ts` / `.svelte.js`    |

Classic stores still work in Svelte 5 for backward compatibility, but runes are the preferred path for new code.

## Best practices

1. **Use getters to expose `$state`** from `.svelte.ts` modules — returning the raw value snapshot breaks reactivity.
2. **Prefer `$derived` over `$effect` + assignment** for computed values; effects are for side effects, not state derivation.
3. **Scope `$.svelte.ts` modules** as factories (`createCounter`) so each consumer gets isolated state, unless you want a shared singleton.
4. **Don't destructure reactive objects** in the consumer — read fields lazily so tracking is preserved.
5. **Name files `.svelte.ts`** whenever you use runes outside a component; plain `.ts` will not compile runes.