import { useActionState } from "react";
import type { ReactElement } from "react";

type ContactInput = { name: string; email: string; message: string };
type FieldErrors = Partial<Record<keyof ContactInput, string>>;

type ContactState =
  | { ok: false; errors: FieldErrors; values: ContactInput }
  | { ok: true };

function validate(input: ContactInput): FieldErrors {
  const errors: FieldErrors = {};
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

async function persistContactMessage(input: ContactInput): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 100));
  console.log("persisted:", input);
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
  return { ok: true };
}

const initial: Extract<ContactState, { ok: false }> = {
  ok: false,
  errors: {},
  values: { name: "", email: "", message: "" },
};

function ContactForm(): ReactElement {
  const [state, formAction, pending] = useActionState<ContactState, FormData>(contactAction, initial);
  const values = state.ok === false ? state.values : initial.values;
  const errors = state.ok === false ? state.errors : {};

  return (
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
  );
}

async function run(): Promise<void> {
  const ok = await contactAction(initial, strToFormData({
    name: "Ada",
    email: "ada@example.com",
    message: "Hello from a verified sender.",
  }));
  console.log("valid submission ->", ok);

  const bad = await contactAction(initial, strToFormData({
    name: "x",
    email: "nope",
    message: "short",
  }));
  console.log("invalid submission ->", bad);

  void ContactForm;
}

function strToFormData(input: ContactInput): FormData {
  const fd = new FormData();
  fd.set("name", input.name);
  fd.set("email", input.email);
  fd.set("message", input.message);
  return fd;
}

void run;
run().catch((error) => {
  console.error(error);
  process.exit(1);
});