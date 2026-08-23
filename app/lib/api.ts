const runtimeApiFallback = typeof window === "undefined"
  ? "http://localhost:8000"
  : window.location.protocol === "http:"
    ? `http://${window.location.hostname}:8000`
    : `${window.location.origin}/api`;
export const API_BASE = (process.env.EXPO_PUBLIC_API_URL || runtimeApiFallback).replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit, attempt = 0): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8000);
  try {
    const res = await fetch(`${API_BASE}${path}`, { credentials: "include", ...init, signal: controller.signal });
    if (!res.ok) {
      const raw = await res.text();
      let detail = raw;
      try { const parsed = JSON.parse(raw); detail = typeof parsed.detail === "string" ? parsed.detail : JSON.stringify(parsed.detail); } catch { /* plain-text response */ }
      throw new Error(detail || `Request failed (${res.status})`);
    }
    return res.json();
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") throw new Error("The API took too long to respond. Is the backend running?");
    if ((!init?.method || init.method === "GET") && attempt === 0 && error instanceof TypeError) {
      await new Promise(resolve => setTimeout(resolve, 300));
      return request<T>(path, init, 1);
    }
    if (error instanceof TypeError) throw new Error("Shakti360 is offline or the API cannot be reached.");
    throw error;
  } finally { clearTimeout(timeout); }
}

export async function post<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function get<T>(path: string): Promise<T> {
  return request<T>(path);
}

export async function authPost<T>(path: string, body: unknown = {}): Promise<T> {
  const csrf = typeof document !== "undefined" ? document.cookie.split("; ").find(row => row.startsWith("shakti_csrf="))?.split("=")[1] : undefined;
  return request<T>(path, { method: "POST", credentials: "include", headers: { "Content-Type": "application/json", ...(csrf ? { "X-CSRF-Token": decodeURIComponent(csrf) } : {}) }, body: JSON.stringify(body) });
}
