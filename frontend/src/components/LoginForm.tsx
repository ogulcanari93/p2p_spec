import { FormEvent, useState } from "react";

type Props = {
  onSubmit: (email: string) => Promise<void>;
};

export function LoginForm({ onSubmit }: Props) {
  const [email, setEmail] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit(email);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h1>Sign in</h1>
      <p style={{ color: "var(--muted)", marginTop: 0 }}>
        Prototype auth: enter your email. New users are registered automatically.
      </p>
      <div className="form-field">
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
        />
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn--primary" disabled={submitting}>
        {submitting ? "Signing in…" : "Continue"}
      </button>
    </form>
  );
}
