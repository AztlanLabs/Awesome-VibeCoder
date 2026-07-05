import { useActionState, StrictMode } from "react";
import { useFormStatus } from "react-dom";
import { createRoot } from "react-dom/client";

interface State {
  error?: string;
  ok?: boolean;
  email?: string;
}

function delay(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

async function signup(_prev: State, formData: FormData): Promise<State> {
  const email = String(formData.get("email") ?? "").trim();
  if (!email) return { error: "Email is required." };
  if (!email.includes("@") || email.length < 5) {
    return { error: "Enter a valid email." };
  }
  await delay(600);
  if (email === "taken@example.com") {
    return { error: "That email is already registered.", email };
  }
  return { ok: true, email };
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return <button type="submit" disabled={pending}>{pending ? "Saving…" : "Save"}</button>;
}

function SignupForm() {
  const [state, formAction, isPending] = useActionState(signup, {});

  return (
    <form action={formAction} method="post">
      <label htmlFor="email">Email</label>
      <input
        id="email"
        name="email"
        type="email"
        defaultValue={state.email}
        aria-invalid={Boolean(state.error)}
        aria-describedby={state.error ? "email-error" : undefined}
      />
      {state.error && <p id="email-error" role="alert">{state.error}</p>}
      {state.ok && <p role="status">Signed up as {state.email} ✓</p>}
      <SubmitButton />
      {isPending && <small>Submitting…</small>}
    </form>
  );
}

function App() {
  return (
    <main>
      <h1>Sign up</h1>
      <SignupForm />
    </main>
  );
}

function describe(): string {
  return [
    "Form Actions",
    "- useActionState(signup, {}) drives the form",
    "- Empty email => 'Email is required.'",
    "- 'ab' => 'Enter a valid email.'",
    "- 'taken@example.com' => 'That email is already registered.'",
    "- valid email => after 600ms { ok: true, email } with success message",
    "- SubmitButton uses useFormStatus for pending label, disabled while saving",
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