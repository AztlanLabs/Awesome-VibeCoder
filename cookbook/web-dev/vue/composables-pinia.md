# Composables & Pinia

Vue 3's Composition API encourages extracting reusable reactive logic into **composables** (`ref`, `computed`, `watchEffect`), and Pinia stores manage app-wide state. This recipe shows a typed composable and a setup-style `defineStore`.

> **Runnable example:** [recipe/composables-pinia.ts](recipe/composables-pinia.ts)
>
> ```bash
> # see recipe README for setup
> ```

## Example scenario

You want a reusable data-fetching composable (`useFetchData`) with `data`/`error`/`loading` refs and automatic refresh, plus a `useCounterStore` Pinia store in setup style that exposes typed getters and actions.

## A typed composable

```ts
import { ref, computed, watchEffect, type Ref } from 'vue';

export function useFetchData<T>(url: Ref<string> | string) {
  const data = ref<T | null>(null);
  const error = ref<Error | null>(null);
  const loading = ref(false);
  const isReady = computed(() => data.value !== null && !error.value);

  async function load() {
    loading.value = true;
    error.value = null;
    try {
      const target = typeof url === 'string' ? url : url.value;
      const res = await fetch(target);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      data.value = (await res.json()) as T;
    } catch (e) {
      error.value = e instanceof Error ? e : new Error(String(e));
    } finally {
      loading.value = false;
    }
  }

  watchEffect(() => {
    if (typeof url !== 'string') load();
  });

  void load();
  return { data, error, loading, isReady, reload: load };
}
```

`Ref<T>` lets callers pass a reactive URL so changing it re-fetches; passing a plain string fetches once.

## Pinia setup-style store

```ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0);
  const double = computed(() => count.value * 2);
  function increment(by = 1) { count.value += by; }
  function reset() { count.value = 0; }
  return { count, double, increment, reset };
});
```

Setup style gives you full TypeScript type inference for getters and actions without the option-store's `state`/`getters`/`actions` object shape.

## Using the store

```ts
import { createPinia } from 'pinia';
const pinia = createPinia();
const store = useCounterStore(pinia);
store.increment(3);
console.log(store.count, store.double);
```

## Best practices

1. **Return refs, not values**, from composables so consumers retain reactivity.
2. **Name composables `useX`** and stores `useYStore` — the `use` prefix is the Vue convention.
3. **Prefer setup-style `defineStore`** for new code; it composes naturally with composables and other stores.
4. **Type the composable's generic** (`<T>`) and narrow with `as` at the boundary, never `any` inside.
5. **Clean up watchers** by returning the stop handle from `watchEffect` when the composable's lifecycle differs from a component.
6. **Install Pinia before calling any store** (`app.use(pinia)`); tests can pass a fresh `createPinia()` to the store factory.