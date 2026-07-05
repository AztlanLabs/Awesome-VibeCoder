# Runnable Recipe Examples — Vue

Minimal example files for each Vue 3.5 cookbook recipe. The `.ts` composable/store file can be type-checked and partially executed with `tsx`; the `.vue` SFC needs `@vue/compiler-sfc` to compile before it can render.

## Prerequisites

- Node.js 18 or later
- Install dependencies:

```bash
npm install
```

## How to use these files

| Recipe               | File                          | How to run                                                                                              |
| -------------------- | ----------------------------- | ------------------------------------------------------------------------------------------------------- |
| Composables & Pinia  | `composables-pinia.ts`        | `npx tsx composables-pinia.ts` runs the `demonstrate()` harness (it bootstraps an active Pinia and logs counter state changes). |
| SFC `<script setup>` | `sfc-script-setup.vue`        | Compile with `@vue/compiler-sfc` (see below) or drop into a Vite/Vue project.                         |

## Running the composables/store harness

```bash
npx tsx composables-pinia.ts
```

## Compiling a single `.vue` SFC

There is no first-class DOM runner for a single SFC, but you can compile and inspect its render output with `@vue/compiler-sfc`:

```ts
import { parse, compileScript, compileTemplate } from '@vue/compiler-sfc';
import { readFileSync } from 'node:fs';

const source = readFileSync('./sfc-script-setup.vue', 'utf8');
const { descriptor } = parse(source, { filename: 'sfc-script-setup.vue' });
const script = compileScript(descriptor, { id: 'demo' });
const { code } = compileTemplate({
  id: 'demo',
  filename: 'sfc-script-setup.vue',
  source: descriptor.template?.content ?? '',
});
console.log('compiled script bindings:', script.bindings);
console.log('render code length:', code.length);
```

Save this as `compile-sfc.mjs` and run with `node compile-sfc.mjs`. For full render/interactivity, use the Vue CLI:

```bash
npm create vue@latest my-app
cd my-app
npm install
npm run dev
```

## Parent Cookbook

See the [parent cookbook README](../README.md).