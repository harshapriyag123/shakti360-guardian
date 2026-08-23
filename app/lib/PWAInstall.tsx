import { useEffect, useMemo, useState } from "react";
import { Linking, Platform, Pressable, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "./ui";

type InstallPrompt = Event & { prompt: () => Promise<void>; userChoice: Promise<{ outcome: "accepted" | "dismissed" }> };

export function PWAInstall() {
  const [prompt, setPrompt] = useState<InstallPrompt | null>(null);
  const [installed, setInstalled] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [notice, setNotice] = useState("");
  const device = useMemo(() => {
    if (Platform.OS !== "web" || typeof navigator === "undefined") return Platform.OS;
    return /iphone|ipad|ipod/i.test(navigator.userAgent) ? "ios" : /android/i.test(navigator.userAgent) ? "android" : "web";
  }, []);
  const androidUrl = process.env.EXPO_PUBLIC_ANDROID_DOWNLOAD_URL;
  const iosUrl = process.env.EXPO_PUBLIC_IOS_DOWNLOAD_URL;

  useEffect(() => {
    if (Platform.OS !== "web") return;
    const media = window.matchMedia("(display-mode: standalone)");
    setInstalled(media.matches);
    const capture = (event: Event) => { event.preventDefault(); setPrompt(event as InstallPrompt); };
    const complete = () => { setInstalled(true); setPrompt(null); };
    window.addEventListener("beforeinstallprompt", capture);
    window.addEventListener("appinstalled", complete);
    return () => { window.removeEventListener("beforeinstallprompt", capture); window.removeEventListener("appinstalled", complete); };
  }, []);

  if (Platform.OS !== "web" || installed) return null;

  async function installWeb() {
    if (prompt) {
      await prompt.prompt();
      const choice = await prompt.userChoice;
      setNotice(choice.outcome === "accepted" ? "Installation started." : "Installation was cancelled.");
      if (choice.outcome === "accepted") setPrompt(null);
      return;
    }
    setNotice(device === "ios" ? "In Safari, tap Share, then Add to Home Screen." : device === "android" ? "Open the browser menu and tap Install app or Add to Home screen." : "Open your browser menu and choose Install Shakti360 or Create shortcut.");
  }

  return <View style={{ borderWidth: 1, borderColor: colors.border, borderRadius: 18, padding: 14, backgroundColor: "white", gap: 12 }}>
    <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}><Ionicons name="download-outline" size={25} color={colors.primary} /><View style={{ flex: 1 }}><Text style={{ color: colors.ink, fontWeight: "900" }}>Get Shakti360 on this device</Text><Text style={{ color: colors.muted, fontSize: 12, marginTop: 2 }}>Install the secure web app now, or choose a native release.</Text></View><Pressable accessibilityRole="button" onPress={() => setExpanded(value => !value)} style={{ padding: 10 }}><Ionicons name={expanded ? "chevron-up" : "chevron-down"} size={21} color={colors.primary} /></Pressable></View>
    {expanded ? <View style={{ gap: 9 }}>
      <Pressable accessibilityRole="button" onPress={installWeb} style={{ backgroundColor: colors.primary, borderRadius: 13, padding: 13 }}><Text style={{ color: "white", fontWeight: "900", textAlign: "center" }}>Install web app {device === "ios" ? "on iPhone/iPad" : device === "android" ? "on Android" : "on this computer"}</Text></Pressable>
      <View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap" }}>
        <Pressable accessibilityRole="link" disabled={!androidUrl} onPress={() => androidUrl && Linking.openURL(androidUrl)} style={{ flex: 1, minWidth: 135, borderWidth: 1, borderColor: colors.border, borderRadius: 13, padding: 12, opacity: androidUrl ? 1 : .55 }}><Text style={{ color: colors.ink, fontWeight: "800", textAlign: "center" }}>Android APK</Text><Text style={{ color: colors.muted, fontSize: 11, textAlign: "center", marginTop: 3 }}>{androidUrl ? "Download signed build" : "Release not published"}</Text></Pressable>
        <Pressable accessibilityRole="link" disabled={!iosUrl} onPress={() => iosUrl && Linking.openURL(iosUrl)} style={{ flex: 1, minWidth: 135, borderWidth: 1, borderColor: colors.border, borderRadius: 13, padding: 12, opacity: iosUrl ? 1 : .55 }}><Text style={{ color: colors.ink, fontWeight: "800", textAlign: "center" }}>iPhone / iPad</Text><Text style={{ color: colors.muted, fontSize: 11, textAlign: "center", marginTop: 3 }}>{iosUrl ? "Open signed release" : "Release not published"}</Text></Pressable>
      </View>
      {notice ? <Text accessibilityLiveRegion="polite" style={{ color: colors.primaryDark, fontSize: 12, lineHeight: 18 }}>{notice}</Text> : null}
    </View> : null}
  </View>;
}
