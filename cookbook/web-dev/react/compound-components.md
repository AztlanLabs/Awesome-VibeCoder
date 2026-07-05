# Compound Components (Accessible Tabs)

Build a Tabs component from `TabList`, `Tab`, and `TabPanel` children that share a context and implement full WAI-ARIA keyboard navigation — no `forwardRef`, refs passed as props.

> **Runnable example:** [recipe/compound-components.tsx](recipe/compound-components.tsx)
>
> ```bash
> cd recipe && npm install
> npx tsx compound-components.tsx
> # or: npm run compound-components
> ```

## Example scenario

A page renders tabbed content. The author composes `<Tabs>` with `<TabList><Tab/></TabList>` and `<TabPanel>` children, without wiring any handlers or IDs themselves.

## Context API

The parent owns the selected index and onChange; children consume it.

```tsx
interface TabsCtx {
  id: string;
  selected: number;
  count: number;
  onSelect: (i: number) => void;
  getTabId: (i: number) => string;
  getPanelId: (i: number) => string;
}
const TabsContext = createContext<TabsCtx | null>(null);
```

## Controlled + uncontrolled

`Tabs` accepts an optional `value` / `onChange` (controlled) and otherwise manages internal state.

```tsx
const [internal, setInternal] = useState(0);
const selected = selected ?? internal;
```

## Keyboard navigation (ARROW / HOME / END)

The `TabList` keeps refs to each tab DOM node and focuses the correct one when the key changes. Per WAI-ARIA, arrows move focus without wrap; Home/End jump to ends.

```tsx
const tabs = Array.from(tabsRef.current!).filter(Boolean) as HTMLButtonElement[];
const onKeyDown = (e: KeyboardEvent) => {
  const last = count - 1;
  let next = selected;
  if (e.key === "ArrowRight") next = Math.min(selected + 1, last);
  if (e.key === "ArrowLeft") next = Math.max(selected - 1, 0);
  if (e.key === "Home") next = 0;
  if (e.key === "End") next = last;
  if (next !== selected) {
    onSelect(next);
    tabs[next]?.focus();
  }
};
```

## Tab and TabPanel

`Tab` accepts a `ref` prop directly (React 19). `id`, `aria-controls`, `role="tab"`, and `aria-selected` come from context.

```tsx
function Tab({ children, ref }: { children: ReactNode; ref?: Ref<HTMLButtonElement> }) {
  // ...
}
```

## Composing the demo

```tsx
<Tabs defaultValue={0}>
  <TabList>
    <Tab>Overview</Tab>
    <Tab>Usage</Tab>
    <Tab>API</Tab>
  </TabList>
  <TabPanel>...overview...</TabPanel>
  <TabPanel>...usage...</TabPanel>
  <TabPanel>...api...</TabPanel>
</Tabs>
```

## Best practices

1. **Generate stable IDs** from a top-level `id` so tabs/panels are linked even if the author doesn't pass IDs.
2. **Hide inactive panels with `hidden`** so they're removed from the a11y tree (not just CSS).
3. **Move focus, not just selection**, on arrow keys — screen-reader users follow the focus ring.
4. **Support both controlled and uncontrolled** usage via a `defaultValue` + optional `value`.
5. **Pass refs as props**, no `forwardRef` — React 19 lets components accept `ref` directly.