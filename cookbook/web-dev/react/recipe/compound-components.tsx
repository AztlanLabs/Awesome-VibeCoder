import {
  Children,
  cloneElement,
  createContext,
  isValidElement,
  useContext,
  useState,
  useRef,
  StrictMode,
  type KeyboardEvent,
  type ReactNode,
  type Ref,
  type ReactElement,
} from "react";
import { createRoot } from "react-dom/client";

interface TabsCtx {
  id: string;
  selected: number;
  count: number;
  onSelect: (i: number) => void;
  getTabId: (i: number) => string;
  getPanelId: (i: number) => string;
}
const TabsContext = createContext<TabsCtx | null>(null);

function useTabs(): TabsCtx {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error("Tabs.* must be rendered inside <Tabs>");
  return ctx;
}

interface TabsProps {
  id?: string;
  defaultValue?: number;
  value?: number;
  onChange?: (i: number) => void;
  children: ReactNode;
}

function Tabs({ id = "tabs", value, defaultValue = 0, onChange, children }: TabsProps) {
  const [internal, setInternal] = useState(defaultValue);
  const controlled = value !== undefined;
  const selected = controlled ? value : internal;

  let panelCount = 0;
  Children.forEach(children, (child) => {
    if (isValidElement(child) && child.type === TabPanel) panelCount += 1;
  });

  const onSelect = (i: number) => {
    if (!controlled) setInternal(i);
    onChange?.(i);
  };

  const ctx: TabsCtx = {
    id,
    selected,
    count: panelCount,
    onSelect,
    getTabId: (i) => `${id}-tab-${i}`,
    getPanelId: (i) => `${id}-panel-${i}`,
  };

  return (
    <div>
      <TabsContext.Provider value={ctx}>{children}</TabsContext.Provider>
    </div>
  );
}

function TabList({
  children,
  ref,
}: {
  children: ReactNode;
  ref?: Ref<HTMLDivElement>;
}) {
  const tabsRef = useRef<(HTMLButtonElement | null)[]>([]);
  const ctx = useTabs();
  const items = Children.toArray(children) as ReactElement[];

  const onKeyDown = (e: KeyboardEvent<HTMLDivElement>) => {
    const last = ctx.count - 1;
    if (last < 0) return;
    let next = ctx.selected;
    if (e.key === "ArrowRight") next = Math.min(ctx.selected + 1, last);
    else if (e.key === "ArrowLeft") next = Math.max(ctx.selected - 1, 0);
    else if (e.key === "Home") next = 0;
    else if (e.key === "End") next = last;
    else return;
    e.preventDefault();
    ctx.onSelect(next);
    tabsRef.current[next]?.focus();
  };

  return (
    <div
      ref={ref}
      role="tablist"
      aria-orientation="horizontal"
      onKeyDown={onKeyDown}
      style={{ display: "flex", gap: 8, borderBottom: "1px solid #ccc" }}
    >
      {items.map((child, i) => {
        if (!isValidElement(child) || child.type !== Tab) {
          return child as ReactNode;
        }
        return cloneElement(child, {
          index: i,
          ref: (el: HTMLButtonElement | null) => {
            tabsRef.current[i] = el;
          },
        } as Partial<TabProps>);
      })}
    </div>
  );
}

interface TabProps {
  index?: number;
  ref?: Ref<HTMLButtonElement>;
  children?: ReactNode;
}

function Tab({ index = 0, ref, children }: TabProps) {
  const ctx = useTabs();
  const selected = ctx.selected === index;
  return (
    <button
      ref={ref}
      role="tab"
      id={ctx.getTabId(index)}
      aria-controls={ctx.getPanelId(index)}
      aria-selected={selected}
      tabIndex={selected ? 0 : -1}
      onClick={() => ctx.onSelect(index)}
      style={{
        padding: "6px 12px",
        background: selected ? "#eee" : "transparent",
        border: "none",
        borderBottom: selected ? "2px solid #0070f3" : "2px solid transparent",
        cursor: "pointer",
      }}
    >
      {children}
    </button>
  );
}

interface PanelProps {
  index?: number;
  ref?: Ref<HTMLDivElement>;
  children?: ReactNode;
}

function TabPanel({ index = 0, ref, children }: PanelProps) {
  const ctx = useTabs();
  if (ctx.selected !== index) return null;
  return (
    <div
      ref={ref}
      role="tabpanel"
      id={ctx.getPanelId(index)}
      aria-labelledby={ctx.getTabId(index)}
      style={{ padding: 12 }}
    >
      {children}
    </div>
  );
}

Tabs.TabList = TabList;
Tabs.Tab = Tab;
Tabs.TabPanel = TabPanel;

function App() {
  return (
    <main>
      <h1>Tabs</h1>
      <Tabs defaultValue={0}>
        <Tabs.TabList>
          <Tabs.Tab>Overview</Tabs.Tab>
          <Tabs.Tab>Usage</Tabs.Tab>
          <Tabs.Tab>API</Tabs.Tab>
        </Tabs.TabList>
        <Tabs.TabPanel>Overview content — high-level intro.</Tabs.TabPanel>
        <Tabs.TabPanel>Usage content — copy the snippet into your app.</Tabs.TabPanel>
        <Tabs.TabPanel>API content — available props above.</Tabs.TabPanel>
      </Tabs>
    </main>
  );
}

function describe(): string {
  return [
    "Compound Components: Accessible Tabs",
    "- <Tabs> owns context (id, selected, count, onSelect)",
    "- TabList renders role='tablist', handles ArrowLeft/ArrowRight/Home/End focusing next tab",
    "- Tab renders role='tab' with id, aria-controls, aria-selected, tabIndex roving",
    "- TabPanel renders role='tabpanel' with id, aria-labelledby; inactive hidden (returns null)",
    "- Default selected tab: 0 => 'Overview content' visible",
  ].join("\n");
}

if (typeof document !== "undefined") {
  createRoot(document.getElementById("root")!).render(
    <StrictMode>
      <App />
    </StrictMode>,
  );
} else {
  console.log(describe());
}