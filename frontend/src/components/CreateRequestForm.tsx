import { FormEvent, useState } from "react";
import { ApiError, createRequest, type CreateRequestResponse } from "../api/client";
import { DestinationSelector } from "./DestinationSelector";

type Props = {
  onCreated: (response: CreateRequestResponse) => void;
};

const NOTE_MAX = 280;

export function CreateRequestForm({ onCreated }: Props) {
  const [recipientContact, setRecipientContact] = useState("");
  const [amount, setAmount] = useState("");
  const [note, setNote] = useState("");
  const [currency] = useState("TRY");
  const [destinationId, setDestinationId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (note.length > NOTE_MAX) {
      setError(`Note must be at most ${NOTE_MAX} characters.`);
      return;
    }

    setSubmitting(true);
    try {
      const res = await createRequest({
        recipient_contact: recipientContact,
        amount,
        currency,
        note: note.trim() || undefined,
        destination_id: destinationId || undefined,
      });
      onCreated(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create request");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h1>Request money</h1>
      <div className="form-field">
        <label htmlFor="recipient">Recipient email or phone</label>
        <input
          id="recipient"
          data-testid="create-recipient"
          required
          value={recipientContact}
          onChange={(e) => setRecipientContact(e.target.value)}
          placeholder="friend@example.com"
        />
        <small style={{ color: "var(--muted)" }}>
          Must be a registered user&apos;s email or phone number.
        </small>
      </div>
      <div className="form-field">
        <label htmlFor="amount">Amount ({currency})</label>
        <input
          id="amount"
          data-testid="create-amount"
          required
          inputMode="decimal"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="100.00"
        />
      </div>
      <DestinationSelector currency={currency} value={destinationId} onChange={setDestinationId} />
      <div className="form-field">
        <label htmlFor="note">Note (optional)</label>
        <textarea
          id="note"
          rows={3}
          maxLength={NOTE_MAX}
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
        <small style={{ color: "var(--muted)" }}>
          {note.length}/{NOTE_MAX}
        </small>
      </div>
      {error && <p className="form-error">{error}</p>}
      <button type="submit" className="btn btn--primary" data-testid="create-submit" disabled={submitting}>
        {submitting ? "Creating…" : "Create request"}
      </button>
    </form>
  );
}
