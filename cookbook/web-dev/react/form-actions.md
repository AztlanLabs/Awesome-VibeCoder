# Form Actions

Drive forms with React 19's `useActionState` and `useFormStatus` against an async, validating "Server-Action-style" function — with progressive enhancement and pending UI for free.

> **Runnable example:** [recipe/form-actions.tsx](recipe/form-actions.tsx)
>
> ```bash
> cd recipe && npm install
> npx tsx form-actions.tsx
> # or: npm run form-actions
> ```

## Example scenario

A signup form must validate input, simulate a slow submission, show inline errors, and keep the submit button disabled with a spinner while in flight — without juggling `isPending`/`error` state by hand.

## The action signature

`useActionState` passes the current state and the submitted `FormData` to the action. Return the next state.

```tsx
type State = { error?: string; ok?: boolean; email?: string };

async function signup(_prev: State, formData: FormData): Promise<State> {
  const email = String(formData.get("email") ?? "");
  if (!email.includes("@")) {
    return { error: "Enter a valid email." };
  }
  await delay(600);
  return { ok: true, email };
}
```

## Hooking it up

```tsx
const [state, formAction, isPending] = useActionState(signup, {});
return (
  <form action={formAction}>
    <input name="email" defaultValue={state.email} />
    {state.error && <p role="alert">{state.error}</p>}
    <SubmitButton />
  </form>
);
```

## Pending UI with `useFormStatus`

Because the button is *inside* the form, `useFormStatus` reflects submission state without prop-drilling.

```tsx
function SubmitButton() {
  const { pending } = useFormStatus();
  return <button disabled={pending}>{pending ? "Saving…" : "Save"}</button>;
}
```

## Progressive enhancement

The form uses a real `action` attribute, so without JS it still POSTs. With JS, React intercepts submission and streams state back into the UI.

```tsx
<form action={formAction} method="post">
```

## Best practices

1. **Keep actions pure and idempotent** — they may run on the server and replay on the client.
2. **Return the whole state from the action**, not just the error, so inputs can restore.
3. **Put pending UI inside the form** so `useFormStatus` works without lifting state.
4. **Reset after success** with a `key` or by returning a fresh state object.
5. **Validate on the server too** — client state is for UX, not security.