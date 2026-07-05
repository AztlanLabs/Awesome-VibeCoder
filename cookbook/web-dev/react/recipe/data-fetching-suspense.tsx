import { Component, Suspense, use, StrictMode, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

type Cache = Map<string, Promise<unknown>>;
const cache: Cache = new Map();

interface Profile {
  id: string;
  name: string;
  role: string;
}

function fakeApi(id: string): Promise<Profile> {
  return new Promise((resolve) => {
    setTimeout(() => resolve({ id, name: `User ${id}`, role: "Engineer" }), 200);
  });
}

function fetchProfile(id: string): Promise<Profile> {
  const cached = cache.get(id);
  if (cached) return cached as Promise<Profile>;
  const p = fakeApi(id).catch((err) => {
    cache.delete(id);
    throw err;
  });
  cache.set(id, p);
  return p;
}

function Profile({ id }: { id: string }) {
  const profile = use(fetchProfile(id));
  return (
    <div>
      <strong>{profile.name}</strong>
      <span> · {profile.role} · id={profile.id}</span>
    </div>
  );
}

interface BoundaryState {
  error: Error | null;
}
interface BoundaryProps {
  children: ReactNode;
  fallback: (retry: () => void) => ReactNode;
}

class ErrorBoundary extends Component<BoundaryProps, BoundaryState> {
  state: BoundaryState = { error: null };

  static getDerivedStateFromError(error: unknown): BoundaryState {
    return { error: error instanceof Error ? error : new Error(String(error)) };
  }

  retry = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      return this.props.fallback(this.retry);
    }
    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary fallback={(retry) => <p>Failed to load. <button onClick={retry}>Retry</button></p>}>
      <main>
        <h1>Profile</h1>
        <Suspense fallback={<p>Loading…</p>}>
          <Profile id="u_42" />
        </Suspense>
      </main>
    </ErrorBoundary>
  );
}

function describe(): string {
  return [
    "Data Fetching with Suspense & use()",
    "- ErrorBoundary wraps the tree",
    "- Suspense fallback: 'Loading…'",
    "- Profile(id=u_42) resolves via fakeApi() => 'User u_42 · Engineer · id=u_42'",
    "- On rejection the boundary fallback shows a Retry button",
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