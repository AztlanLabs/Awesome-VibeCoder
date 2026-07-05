import {
  Component,
  StrictMode,
  Suspense,
  useCallback,
  useState,
  type ReactNode,
} from "react";
import { createRoot } from "react-dom/client";

interface ErrorInfo {
  componentStack: string;
}
interface BoundaryProps {
  resetKey?: unknown;
  onError?: (error: Error, info: ErrorInfo) => void;
  fallback: (error: Error, reset: () => void) => ReactNode;
  children: ReactNode;
}
interface BoundaryState {
  error: Error | null;
}

class ErrorBoundary extends Component<BoundaryProps, BoundaryState> {
  state: BoundaryState = { error: null };

  static getDerivedStateFromError(error: unknown): BoundaryState {
    return { error: error instanceof Error ? error : new Error(String(error)) };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    this.props.onError?.(error, info);
  }

  reset = (): void => this.setState({ error: null });

  componentDidUpdate(prev: BoundaryProps): void {
    if (this.state.error && this.props.resetKey !== prev.resetKey) {
      this.reset();
    }
  }

  render(): ReactNode {
    if (this.state.error) {
      return this.props.fallback(this.state.error, this.reset);
    }
    return this.props.children;
  }
}

function useErrorReporter(): (error: Error, info: ErrorInfo) => void {
  return useCallback((error: Error, info: ErrorInfo) => {
    console.error("[telemetry]", error.message, info.componentStack);
  }, []);
}

function Fallback({ error, reset }: { error: Error; reset: () => void }): ReactNode {
  return (
    <div role="alert">
      <p>Something broke: {error.message}</p>
      <button onClick={reset}>Retry</button>
    </div>
  );
}

function FallbackAdapter(error: Error, reset: () => void): ReactNode {
  return <Fallback error={error} reset={reset} />;
}

interface BuggyProps {
  id: number;
}
function BuggyWidget({ id }: BuggyProps): ReactNode {
  if (id % 2 === 0) {
    throw new Error(`Widget ${id} is malformed`);
  }
  return <p>Widget {id} rendered OK.</p>;
}

function App(): ReactNode {
  const [id, setId] = useState(1);
  const report = useErrorReporter();

  return (
    <main>
      <h1>Record viewer</h1>
      <p>Current id: {id}</p>
      <button onClick={() => setId((i) => i + 1)}>Next record</button>
      <hr />
      <ErrorBoundary
        resetKey={id}
        onError={report}
        fallback={FallbackAdapter}
      >
        <Suspense fallback={<p>Loading…</p>}>
          <BuggyWidget id={id} />
        </Suspense>
      </ErrorBoundary>
    </main>
  );
}

function describe(): string {
  return [
    "Error Boundaries",
    "- ErrorBoundary catches BuggyWidget render errors",
    "- resetKey=id => toggling to a new id clears the fallback automatically",
    "- onError logs to console (useErrorReporter)",
    "- id=1 OK, id=2 throws 'Widget 2 is malformed', id=3 OK again after reset",
    "- Fallback shows Retry button wired to reset()",
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