# SFC `<script setup>`

Vue 3.5's `<script setup>` compiles to optimized render code and exposes compile-time macros (`defineProps`, `defineEmits`, `defineModel`, `defineExpose`, `useTemplateRef`) plus typed `provide`/`inject`.

> **Runnable example:** [recipe/sfc-script-setup.vue](recipe/sfc-script-setup.vue)
>
> ```bash
> # see recipe README for setup
> ```

## Example scenario

A `Counter` child component receives an initial value via prop, v-models its current count up to a parent, exposes an imperative `reset()` method, and consumes a theme injected by an ancestor.

## Props, emits, and `defineModel`

```vue
<script setup lang="ts">
const props = defineProps<{ initial?: number; label: string }>();
const emit = defineEmits<{ 'update:count': [value: number]; submit: [] }>();
const count = defineModel<number>('count', { default: props.initial ?? 0 });
</script>
```

`defineModel` auto-wires the `v-model:count` two-way binding; `defineEmits` with the tuple-of-args signature gives you fully typed payload access.

## `useTemplateRef`

In Vue 3.5, `useTemplateRef('name')` returns a typed ref bound to `ref="name"` in the template, removing the need to declare a ref ahead of template usage.

```ts
const inputEl = useTemplateRef<HTMLInputElement>('inputEl');
onMounted(() => inputEl.value?.focus());
```

## Typed `provide` / `inject`

```ts
import type { InjectionKey, Ref } from 'vue';

export const themeKey: InjectionKey<Ref<string>> = Symbol('theme');

const theme = inject(themeKey, ref('light'));
```

Providers inject with `provide(themeKey, ref('dark'))`. The `InjectionKey<T>` makes the contract type-safe — `inject` returns `Ref<string> | undefined`.

## `defineExpose`

```ts
defineExpose({ reset, increment });
```

Parents can call `(childRef.value as InstanceType<typeof Counter>).reset()` — `defineExpose` whitelists the surface.

## Best practices

1. **Type `defineProps` and `defineEmits` with object-literal generics** (`defineProps<{...}>`) for full inference without `withDefaults` boilerplate in most cases.
2. **Use `defineModel` for any child-owned value that the parent wants to v-model**; avoid hand-rolling prop+emit pairs.
3. **Always pair `useTemplateRef` with a typed element** (`HTMLInputElement`) so template usage is checked.
4. **Use `InjectionKey<T>` for every provide/inject pair** — the symbol is the unique key and `T` is the contract.
5. **Keep `defineExpose` minimal**; only expose imperative APIs the parent truly needs to call.
6. **Top imports first**, then macros — macros are compiler-only and don't need importing.