# Server Actions Validation

Validate a Server Action's input with a hand-rolled Zod-style schema (no extra dependency), drive the form with `useActionState`, and provide progressive enhancement so the form still works without JavaScript.

> **Runnable example:** [recipe/server-actions-validation.tsx](recipe/server-actions-validation.tsx)
>
> ```bash
> cd recipe && npm install
> npx tsx server-actions-validation.tsx
> # or: npm run server-actions-validation
> ```

## Example scenario

You have a "contact" form (`name`, `email`, `message`) that must be validated server-side before mutating state. You want:

- One typed `prevState` shape shared between the action and the client.
- Per-field error messages surfaced next to inputs.
- A success toast when the action succeeds.
- The form to keep working even if JS is disabled (progressive enhancement).

## Schema (hand-rolled, no `zod`)

```ts
// app/actions/contact.ts
import { redirect } from "next/navigation";

export type ContactState = {
  ok: false;
  errors: Partial<Record<"name" | "email" | "message", string>>;
  values: { name: string; email: string; message: string };
} | {
  ok: true;
};

type ContactInput = { name: string; email: string; message: string };

function validate(input: ContactInput): Partial<Record<keyof ContactInput, string>> {
  const errors: Partial<Record<keyof ContactInput, string>> = {};
  const name = input.name.trim();
  const email = input.email.trim();
  const message = input.message.trim();

  if (name.length < 2) errors.name = "Name must be at least 2 characters.";
  if (email.length === 0 || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    errors.email = "Enter a valid email address.";
  }
  if (message.length < 10) errors.message = "Message must be at least 10 characters.";
  return errors;
}

export async function contactAction(prevState: ContactState, formData: FormData): Promise<ContactState> {
  const input: ContactInput = {
    name: String(formData.get("name") ?? ""),
    email: String(formData.get("email") ?? ""),
    message: String(formData.get("message") ?? ""),
  };
  const errors = validate(input);
  if (Object.keys(errors).length > 0) {
    return { ok: false, errors, values: input };
  }

  await persistContactMessage(input);
  // For a true progressive-enhancement POST, redirect only on success:
  // redirect("/contact/thanks");
  return { ok: true };
}

async function persistContactMessage(input: ContactInput): Promise<void> {
  // Replace with your DB call.
  await new Promise((resolve) => setTimeout(resolve, 200));
  console.log("persisted", input);
}
```

## Client component

`"use client"` is required because `useActionState` is a hook. The surrounding page can stay a Server Component and import this component directly — **never use `next/dynamic` with `{ ssr: false }` inside a Server Component**; just import the client component.

```tsx
// app/contact/ContactForm.tsx
"use client";

import { useActionState, useEffect, useRef, useState } from "react";
import { contactAction, type ContactState } from "../actions/contact";

const initial: ContactState = {
  ok: false,
  errors: {},
  values: { name: "", email: "", message: "" },
};

export function ContactForm() {
  const [state, formAction, pending] = useActionState<ContactState, FormData>(contactAction, initial);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (state.ok) {
      setToast("Message sent — thanks!");
      toastTimer.current = setTimeout(() => setToast(null), 4000);
    }
    return () => {
      if (toastTimer.current) clearTimeout(toastTimer.current);
    };
  }, [state.ok]);

  const failed = state.ok === false;
  const values = failed ? state.values : initial.values;
  const errors = failed ? state.errors : {};

  return (
    <div>
      {toast && <div role="status" aria-live="polite">{toast}</div>}
      <form action={formAction} noValidate>
        <label>
          Name
          <input name="name" defaultValue={values.name} aria-invalid={Boolean(errors.name)} />
        </label>
        {errors.name && <p role="alert">{errors.name}</p>}

        <label>
          Email
          <input name="email" type="email" defaultValue={values.email} aria-invalid={Boolean(errors.email)} />
        </label>
        {errors.email && <p role="alert">{errors.email}</p>}

        <label>
          Message
          <textarea name="message" defaultValue={values.message} aria-invalid={Boolean(errors.message)} />
        </label>
        {errors.message && <p role="alert">{errors.message}</p>}

        <button type="submit" disabled={pending}>{pending ? "Sending…" : "Send"}</button>
      </form>
    </div>
  );
}
```

## Page (Server Component)

```tsx
// app/contact/page.tsx
import { ContactForm } from "./ContactForm";

export default function Page() {
  return (
    <main>
      <h1>Contact</h1>
      <ContactForm />
    </main>
  );
}
```

## Progressive enhancement

`<form action={formAction}>` falls back to a standard multipart POST when JavaScript does not load, so the server action still runs. Keep `redirect()` calls inside the action only on the success path to preserve this behavior. Do not gate the submit with client-only `onClick` handlers.

## Best practices

- **Always validate on the server**, even if you also validate on the client. Client validation is UX, not security.
- **Type `prevState` explicitly** — pass `useActionState<ContactState, FormData>` so the action signature is checked at compile time.
- **Return submitted values** on error so the form stays filled (note `defaultValue` reads from `prevState`, not React state, so the field keeps the user's input).
- **Re-run effect on `state.ok`**, not `state`, to avoid re-showing the toast on unrelated re-renders.
- **Never call `any`**; the `prevState` discriminated union (ok/failed) keeps the narrowing type-safe.
- **Avoid importing `zod`** at runtime for small forms — a hand-rolled validator keeps the bundle smaller and the example dependency-free.
- **Do not use `next/dynamic({ ssr: false })` in a Server Component.** Just import the Client Component directly.