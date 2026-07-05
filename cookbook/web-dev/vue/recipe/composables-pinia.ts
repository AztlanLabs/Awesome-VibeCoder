import { createPinia, defineStore, setActivePinia } from 'pinia';
import { ref, computed, watchEffect, type Ref } from 'vue';

export function useFetchData<T>(url: Ref<string> | string) {
  const data: Ref<T | null> = ref(null);
  const error = ref<Error | null>(null);
  const loading = ref(false);
  const isReady = computed(() => data.value !== null && !error.value);

  async function load(): Promise<void> {
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
    if (typeof url !== 'string') void load();
  });

  void load();
  return { data, error, loading, isReady, reload: load };
}

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0);
  const double = computed(() => count.value * 2);

  function increment(by = 1): void {
    count.value += by;
  }

  function reset(): void {
    count.value = 0;
  }

  return { count, double, increment, reset };
});

export async function demonstrate(): Promise<void> {
  setActivePinia(createPinia());
  const store = useCounterStore();
  store.increment(3);
  console.assert(store.count === 3, 'expected 3');
  console.assert(store.double === 6, 'expected 6');
  store.increment(2);
  console.assert(store.count === 5, 'expected 5');
  store.reset();
  watchEffect(() => console.log('[counter] count =', store.count));
}

demonstrate().catch((err) => {
  console.error(err);
  process.exit(1);
});