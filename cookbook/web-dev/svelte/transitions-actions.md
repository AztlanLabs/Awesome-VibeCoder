# Transitions & Actions

Animate elements entering and leaving the DOM with Svelte's transition primitives (`fade`, `slide`, `fly`, `crossfade`, custom `tick`/easing), and extend plain DOM nodes with reusable behavior via **Actions** (`use:`).

> **Runnable example:** [recipe/transitions-actions.svelte](recipe/transitions-actions.svelte)
>
> ```bash
> # see recipe README for setup
> ```

## Example scenario

A todo list where items fly in when added, fade out when removed, and the input is autofocus-extended with a tiny reusable action you can drop into any element.

## Built-in transitions

`fade`, `slide`, `fly`, `scale` come from `svelte/transition`. Each accepts `{ delay, duration, easing }`.

```svelte
<script lang="ts">
  import { fade, fly, slide } from 'svelte/transition';
</script>

{#each items as item (item.id)}
  <li transition:fly={{ y: 10, duration: 200 }}>
    {item.text}
    <button onclick={() => remove(item.id)} aria-label="Remove">✕</button>
  </li>
{/each}
```

Use `in:` / `out:` if you want asymmetric enter/leave, or `transition:` for symmetric. `animate:` runs during keyed `{#each}` reordering (use `flip` for smooth shuffles).

## `crossfade` between containers

`crossfade` returns paired `send` / `receive` transitions, so an item flying from list A appears as entering list B.

```ts
import { crossfade } from 'svelte/transition';
const [send, receive] = crossfade({ duration: 250 });
```

Apply `in:receive` / `out:send` on both containers.

## Custom `tick` & easing

A transition is a function `(node, params, options) => { delay, duration, css(t, u) | tick(t) }`, where `t` goes 0→1 on enter and 1→0 on leave.

```ts
function spin(node: Element, { duration = 400 }: { duration?: number }) {
  return {
    duration,
    css: (t: number) => `
      transform: rotate(${360 * (1 - t)}deg) scale(${t});
      opacity: ${t};
    `,
  };
}
```

Easing functions from `svelte/easing` (e.g. `cubicOut`) shape `t` over time.

## Svelte Actions

An action is a function `(node, params) => { update?, destroy? }` that imperatively touches a DOM node.

```ts
export function autofocus(node: HTMLElement) {
  node.focus();
}
export function clickOutside(node: HTMLElement, callback: () => void) {
  const handler = (e: MouseEvent) => {
    if (!node.contains(e.target as Node)) callback();
  };
  document.addEventListener('click', handler);
  return {
    destroy() {
      document.removeEventListener('click', handler);
    },
    update() {},
  };
}
```

```svelte
<input use:autofocus />
<div use:clickOutside={() => (open = false)}>Modal</div>
```

## Best practices

1. **Prefer `in:`/`out:` over `transition:`** when durations differ, so you can speed up leave animations.
2. **Keep transitions subtle** (~150–250ms); honor `prefers-reduced-motion` and gate animations behind a media query check.
3. **Use keyed `{#each}`** (`(item.id)`) so transitions reliably follow an element across reorders.
4. **Return cleanup from actions** — `destroy()` removes listeners, aborts timers, detaches observers.
5. **Type action params** with optional defaults so components can pass partial config.
6. **Don't put business logic in transitions** — they're pure visual; data state belongs outside `css`/`tick`.