<script lang="ts">
  import { fade, fly, flip } from 'svelte/transition';
  import { cubicOut } from 'svelte/easing';

  type Todo = { id: number; text: string };

  function clickOutside(node: HTMLElement, onOutside: () => void) {
    const handler = (e: MouseEvent) => {
      if (!node.contains(e.target as Node)) onOutside();
    };
    document.addEventListener('click', handler);
    return {
      destroy() {
        document.removeEventListener('click', handler);
      },
      update() {},
    };
  }

  function autofocus(node: HTMLElement) {
    node.focus();
  }

  let nextId = 1;
  let items: Todo[] = $state([]);
  let draft = $state('');

  function add() {
    const text = draft.trim();
    if (!text) return;
    items = [...items, { id: nextId++, text }];
    draft = '';
  }

  function remove(id: number) {
    items = items.filter((t) => t.id !== id);
  }

  let open = $state(false);
</script>

<div use:clickOutside={() => (open = false)}>
  <input bind:value={draft} placeholder="New todo" use:autofocus />
  <button onclick={add}>Add</button>

  <button onclick={() => (open = !open)}>Menu {open ? '▲' : '▼'}</button>
  {#if open}
    <div transition:fly={{ y: -8, duration: 150, easing: cubicOut }}>
      Click outside to close.
    </div>
  {/if}

  <ul>
    {#each items as todo (todo.id)}
      <li transition:fly={{ y: 10, duration: 200 }} animate:flip={{ duration: 150 }}>
        <span>{todo.text}</span>
        <button onclick={() => remove(todo.id)} aria-label="Remove {todo.text}">✕</button>
      </li>
    {:else}
      <p in:fade={{ duration: 120 }}>No items yet.</p>
    {/each}
  </ul>
</div>