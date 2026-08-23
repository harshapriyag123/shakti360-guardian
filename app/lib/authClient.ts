import { authPost, get } from "./api";

export async function getCurrentUser<T>(): Promise<T> {
  try { return (await get<{ user: T }>("/auth/me")).user; }
  catch (firstError) {
    try { await authPost("/auth/refresh"); return (await get<{ user: T }>("/auth/me")).user; }
    catch { throw firstError; }
  }
}
