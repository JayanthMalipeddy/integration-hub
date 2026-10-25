export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
  ) {
    super(message);
  }
}
let accessToken = "";
export async function api(path: string, options: RequestInit = {}) {
  const timeout = AbortSignal.timeout(30000);
  const signal = options.signal
    ? AbortSignal.any([options.signal, timeout])
    : timeout;
  const headers = new Headers(options.headers);
  if (!(options.body instanceof FormData) && !headers.has("Content-Type"))
    headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", "Bearer " + accessToken);
  let response: Response;
  try {
    response = await fetch("/api" + path, { ...options, signal, headers });
  } catch (error) {
    if (options.signal?.aborted) throw error;
    if (timeout.aborted)
      throw new ApiError(
        options.method && options.method !== "GET"
          ? "The request timed out and may still be processing. Refresh the workspace before retrying this action."
          : "The server took too long to respond. Please try refreshing the workspace.",
        0,
      );
    throw new ApiError(
      "Unable to reach the server. Check your connection and try again.",
      0,
    );
  }
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new ApiError(
      typeof data.detail === "string"
        ? data.detail
        : `Request failed (${response.status})`,
      response.status,
    );
  }
  return response.json();
}
export function setAccessToken(value: string) {
  accessToken = value;
}
export function authorizationHeaders(): Record<string, string> {
  return accessToken ? { Authorization: "Bearer " + accessToken } : {};
}
