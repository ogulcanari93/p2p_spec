const AUTH_EMAIL_KEY = "p2p_auth_email";

export function getStoredEmail(): string | null {
  return localStorage.getItem(AUTH_EMAIL_KEY);
}

export function setStoredEmail(email: string): void {
  localStorage.setItem(AUTH_EMAIL_KEY, email);
}

export function clearStoredEmail(): void {
  localStorage.removeItem(AUTH_EMAIL_KEY);
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((d: { msg?: string }) => d.msg ?? JSON.stringify(d)).join(", ");
    }
  } catch {
    /* ignore */
  }
  return res.statusText || "Request failed";
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const headers = new Headers(options.headers);
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  const email = getStoredEmail();
  if (email) {
    headers.set("X-User-Email", email);
  }

  const res = await fetch(path, { ...options, headers });
  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return res.json() as Promise<T>;
}

export type User = {
  id: string;
  email: string;
  display_name: string | null;
  phone: string | null;
  created_at: string;
};

export type PaymentDestination = {
  id: string;
  destination_type: string;
  currency: string;
  display_label: string;
  masked_identifier: string | null;
  status: string;
  is_default: boolean;
};

export type PaymentRequestSummary = {
  id: string;
  share_token: string;
  status: string;
  amount_minor: number;
  currency: string;
  note: string | null;
  recipient_contact: string;
  counterparty_label: string;
  created_at: string;
  expires_at: string;
};

export type PaymentRequestDetail = PaymentRequestSummary & {
  share_url: string;
};

export type CreateRequestResponse = {
  request: PaymentRequestDetail;
  share_url: string;
};

export function login(email: string) {
  return apiFetch<{ user: User }>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function fetchMe() {
  return apiFetch<User>("/api/auth/me");
}

export function fetchDestinations() {
  return apiFetch<PaymentDestination[]>("/api/payment-destinations/me");
}

export function createRequest(payload: {
  recipient_contact: string;
  amount: string;
  currency?: string;
  note?: string;
  destination_id?: string;
}) {
  return apiFetch<CreateRequestResponse>("/api/requests", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function fetchOutgoingRequests() {
  return apiFetch<{ outgoing: PaymentRequestSummary[]; incoming: PaymentRequestSummary[] }>(
    "/api/requests?direction=outgoing",
  );
}
