import { useEffect, useState } from "react";
import { Platform, Pressable, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "./ui";

type InstallPrompt = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: "accepted" | "dismissed" }> };
export function PWAInstall() {
  const [prompt, setPrompt] = useState<InstallPrompt | null>(null); const [installed, setInstalled] = useState(false);
  useEffect(() => { if (Platform.OS !== "web") return; const media = window.matchMedia("(display-mode: standalone)"); setInstalled(media.matches); const capture = (event: Event) => { event.preventDefault(); setPrompt(event as InstallPrompt); }; const complete = () => { setInstalled(true); setPrompt(null); }; window.addEventListener("beforeinstallprompt", capture); window.addEventListener("appinstalled", complete); return () => { window.removeEventListener("beforeinstallprompt", capture); window.removeEventListener("appinstalled", complete); }; }, []);
  if (Platform.OS !== "web" || installed) return null;
  async function install() { if (!prompt) return; await prompt.prompt(); const choice = await prompt.userChoice; if (choice.outcome === "accepted") setPrompt(null); }
  return <View style={{ borderWidth: 1, borderColor: colors.border, borderRadius: 16, padding: 14, backgroundColor: "white", flexDirection: "row", alignItems: "center", gap: 12 }}><Ionicons name="download-outline" size={24} color={colors.primary} /><View style={{ flex: 1 }}><Text style={{ color: colors.ink, fontWeight: "900" }}>Install Shakti360</Text><Text style={{ color: colors.muted, fontSize: 12, marginTop: 2 }}>{prompt ? "Use it like an app, with a resilient offline shell." : "Use your browser menu and choose Add to Home Screen."}</Text></View>{prompt ? <Pressable accessibilityRole="button" onPress={install} style={{ backgroundColor: colors.primary, borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10 }}><Text style={{ color: "white", fontWeight: "800" }}>Install</Text></Pressable> : null}</View>;
}
