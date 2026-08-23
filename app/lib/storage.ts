import AsyncStorage from "@react-native-async-storage/async-storage";

const PREFIX = "shakti360:v1:";
export const storageKeys = { activeJourney: `${PREFIX}active-journey`, dailyNote: `${PREFIX}daily-note`, pendingEvents: `${PREFIX}pending-events`, privacyReceipts: `${PREFIX}privacy-receipts` } as const;

export async function readLocal<T>(key: string): Promise<T | null> {
  try { const value = await AsyncStorage.getItem(key); return value ? JSON.parse(value) as T : null; } catch { return null; }
}
export async function writeLocal<T>(key: string, value: T): Promise<boolean> {
  try { await AsyncStorage.setItem(key, JSON.stringify(value)); return true; } catch { return false; }
}
export async function removeLocal(key: string): Promise<void> { try { await AsyncStorage.removeItem(key); } catch { /* best effort */ } }

type PendingEvent = { id: string; name: string; createdAt: string };
export async function queueNonSensitiveEvent(name: string): Promise<void> {
  const allowed = new Set(["journey.completed", "feedback.pending", "readiness.completed"]);
  if (!allowed.has(name)) return;
  const events = await readLocal<PendingEvent[]>(storageKeys.pendingEvents) ?? [];
  events.push({ id: `${Date.now()}-${Math.random().toString(16).slice(2)}`, name, createdAt: new Date().toISOString() });
  await writeLocal(storageKeys.pendingEvents, events.slice(-50));
}
