export type HealthResponse = {
  status: string;
  service: string;
};

export type ApiError = {
  error: {
    code: string;
    message: string;
  };
};

const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    headers: { Accept: "application/json" },
    cache: "no-store",
  });

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
