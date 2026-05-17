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

export type Wallet = {
  id: string;
  currency: string;
  wallet_type: string;
  display_name: string | null;
  balance_minor: number;
  available_balance_minor: number;
  status: string;
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

export type DestinationSnapshot = {
  destination_type: string;
  display_label: string;
  masked_identifier: string | null;
  currency: string;
};

export type PaymentRequestSummary = {
  id: string;
  share_token: string;
  status: string;
  amount_minor: number;
  currency: string;
  note: string | null;
  recipient_contact: string;
  recipient_contact_type: string;
  counterparty_label: string;
  destination_snapshot: DestinationSnapshot;
  created_at: string;
  expires_at: string;
  is_expired: boolean;
  can_pay: boolean;
  can_decline: boolean;
  can_cancel: boolean;
};

export type Sender = {
  id: string;
  email: string;
  display_name: string | null;
};

export type RequestEvent = {
  id: string;
  event_type: string;
  previous_status: string | null;
  new_status: string | null;
  created_at: string;
  actor_user_id: string | null;
};

export type PaymentRequestDetail = PaymentRequestSummary & {
  sender: Sender | null;
  recipient_user_id: string | null;
  paid_at: string | null;
  declined_at: string | null;
  cancelled_at: string | null;
  expired_at: string | null;
  share_url: string;
  events: RequestEvent[];
};

export type PublicShareView = {
  status: string;
  amount_minor: number;
  currency: string;
  note: string | null;
  sender_display: string;
  recipient_contact_masked: string;
  created_at: string;
  expires_at: string;
  share_token: string;
};

export type CreateRequestResponse = {
  request: PaymentRequestDetail;
  share_url: string;
};

export type PaymentRequestList = {
  outgoing: PaymentRequestSummary[];
  incoming: PaymentRequestSummary[];
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

export function fetchWallet() {
  return apiFetch<Wallet>("/api/wallets/me");
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

export function fetchRequestDetail(id: string) {
  return apiFetch<PaymentRequestDetail>(`/api/requests/${id}`);
}

export function payRequest(id: string) {
  return apiFetch<PaymentRequestDetail>(`/api/requests/${id}/pay`, { method: "POST" });
}

export function declineRequest(id: string) {
  return apiFetch<PaymentRequestDetail>(`/api/requests/${id}/decline`, { method: "POST" });
}

export function cancelRequest(id: string) {
  return apiFetch<PaymentRequestDetail>(`/api/requests/${id}/cancel`, { method: "POST" });
}

export function fetchPublicShare(shareToken: string) {
  return apiFetch<PublicShareView>(`/api/share/${shareToken}`);
}

export function fetchRequests(params?: {
  direction?: string;
  status?: string;
  search?: string;
}) {
  const qs = new URLSearchParams();
  if (params?.direction) qs.set("direction", params.direction);
  if (params?.status && params.status !== "all") qs.set("status", params.status);
  if (params?.search) qs.set("search", params.search);
  const query = qs.toString();
  return apiFetch<PaymentRequestList>(`/api/requests${query ? `?${query}` : ""}`);
}

/** @deprecated Use fetchRequests instead */
export function fetchOutgoingRequests() {
  return fetchRequests({ direction: "outgoing" });
}
