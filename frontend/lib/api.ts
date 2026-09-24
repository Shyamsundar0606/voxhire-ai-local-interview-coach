export type HealthResponse = {
  status: string;
  service: string;
};

export type User = {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
};

export type ApiError = {
  error: {
    code: string;
    message: string;
  };
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  retryAfterRefresh = true,
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers,
    cache: "no-store",
    credentials: "include",
  });

  if (response.status === 401 && retryAfterRefresh && path !== "/auth/refresh") {
    try {
      await refreshAccessToken();
      return request<T>(path, options, false);
    } catch {
      setAccessToken(null);
    }
  }

  if (!response.ok) {
    let message = `Request failed with status ${response.status}.`;
    try {
      const body = (await response.json()) as ApiError;
      message = body.error?.message ?? message;
    } catch {
      // Keep the status-based message when the server response is not JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as T;
}

export function getHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export async function register(email: string, password: string) {
  const result = await request<TokenResponse>("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }, false);
  setAccessToken(result.access_token);
  return result;
}

export async function login(email: string, password: string) {
  const result = await request<TokenResponse>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  }, false);
  setAccessToken(result.access_token);
  return result;
}

export async function refreshAccessToken() {
  const result = await request<TokenResponse>("/auth/refresh", {
    method: "POST",
  }, false);
  setAccessToken(result.access_token);
  return result;
}

export async function logout() {
  try {
    await request<{ status: string }>("/auth/logout", { method: "POST" }, false);
  } finally {
    setAccessToken(null);
  }
}

export function getCurrentUser() {
  return request<User>("/auth/me");
}
