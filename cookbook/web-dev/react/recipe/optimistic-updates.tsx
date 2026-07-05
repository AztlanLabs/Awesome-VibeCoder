import {
  useOptimistic,
  useTransition,
  useState,
  StrictMode,
  type FormEvent,
} from "react";
import { createRoot } from "react-dom/client";

interface Message {
  id: string;
  text: string;
  status: "pending" | "saved" | "error";
}
type OptimisticInput = Omit<Message, "status">;

const api = {
  post(text: string): Promise<Message> {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        if (text.toLowerCase() === "boom") reject(new Error("network down"));
        else resolve({ id: `s_${Date.now()}`, text, status: "saved" });
      }, 400);
    });
  },
};

function OptimisticList({
  messages,
  optimistic,
}: {
  messages: Message[];
  optimistic: Message[];
}) {
  return (
    <ul>
      {optimistic.map((m, i) => (
        <li
          key={m.id + i}
          style={{ opacity: m.status === "pending" ? 0.6 : 1 }}
          aria-busy={m.status === "pending"}
        >
          {m.text}
          {m.status === "pending" && " …"}
          {m.status === "error" && " ✗"}
        </li>
      ))}
      {messages.length === 0 && optimistic.length === 0 && <li>No messages yet.</li>}
    </ul>
  );
}

function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [optimistic, addOptimistic] = useOptimistic<Message[], OptimisticInput>(
    messages,
    (state, msg) => [...state, { ...msg, status: "pending" }],
  );
  const [isPending, startTransition] = useTransition();
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);

  function send(value: string) {
    startTransition(async () => {
      const tempId = `t_${Date.now()}`;
      addOptimistic({ id: tempId, text: value });
      try {
        const saved = await api.post(value);
        setMessages((m) => [...m, saved]);
      } catch {
        setError("Failed to send — try again.");
      }
    });
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    const value = text.trim();
    if (!value || isPending) return;
    setError(null);
    send(value);
    setText("");
  }

  return (
    <section>
      <h1>Chat</h1>
      <OptimisticList messages={messages} optimistic={optimistic} />
      <form onSubmit={onSubmit}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Type a message… (try 'boom' to fail)"
          disabled={isPending}
        />
        <button type="submit" disabled={isPending || !text.trim()}>
          Send
        </button>
      </form>
      {error && <p role="alert">{error}</p>}
      {isPending && <small>sending…</small>}
    </section>
  );
}

function App() {
  return <Chat />;
}

function describe(): string {
  return [
    "Optimistic Updates",
    "- useOptimistic prepends a pending copy of each new message",
    "- useTransition wraps the async post",
    "- api.post resolves after 400ms => message becomes 'saved'",
    "- typing 'boom' rejects => optimistic copy discarded, error shown",
    "- input stays responsive because the work is non-urgent",
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