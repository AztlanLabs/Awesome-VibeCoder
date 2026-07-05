# Web Development Cookbook — Vue

Short, practical recipes for **Vue 3.5 + TypeScript** patterns: Composition API composables (`ref`/`computed`/`watchEffect`), Pinia setup-style stores, and `<script setup>` with `defineProps`/`defineEmits`/`defineModel`/`provide`+`inject`. These recipes focus on framework idioms; running a full Vue app requires the official Vue CLI (`npm create vue@latest`).

Each recipe is concise, copy-pasteable, and links to a runnable example in [`recipe/`](recipe/).

## Recipes

- [Composables & Pinia](composables-pinia.md): `ref`/`computed`/`watchEffect` composables plus a Pinia `defineStore` setup-style store with typed getters and actions.
- [SFC `<script setup>`](sfc-script-setup.md): `defineProps`/`defineEmits`/`defineModel` (v-model on components), `useTemplateRef`, typed `provide`/`inject`.

## Running Notes

Full Vue execution (SFC compilation, reactivity in a Vue runtime) requires `@vue/compiler-sfc` and a Vite/Webpack build. Boot a project with:

```bash
npm create vue@latest
```

The runnable files in `recipe/` are minimal snippets. `.ts` composables/stores can be type-checked directly; the `.vue` SFC needs `@vue/compiler-sfc` to compile (see [recipe/README.md](recipe/README.md) for the single-SFC compile step).

## Contributing

Add a new recipe by creating a markdown file in this folder and a matching file in `recipe/`. Follow repository guidance in [CONTRIBUTING.md](../../../CONTRIBUTING.md).