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
  const hasNativeRelease = Boolean(androidUrl || iosUrl);

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
    setNotice(device === "ios" ? "In Safari: tap Share ⎋, choose Add to Home Screen, then tap Add." : device === "android" ? "In Chrome: tap ⋮, choose Install app or Add to Home screen, then confirm." : "In Chrome or Edge: click the install icon in the address bar. You can also open the ⋮ menu and choose Install Shakti360.");
  }

  return <View style={{ borderWidth: 1, borderColor: colors.border, borderRadius: 18, padding: 14, backgroundColor: "white", gap: 12 }}>
    <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}><Ionicons name="download-outline" size={25} color={colors.primary} /><View style={{ flex: 1 }}><Text style={{ color: colors.ink, fontWeight: "900" }}>Install Shakti360</Text><Text style={{ color: colors.muted, fontSize: 12, marginTop: 2 }}>Add the web app to this {device === "ios" ? "iPhone or iPad" : device === "android" ? "Android device" : "computer"}—no app store required.</Text></View><Pressable accessibilityRole="button" onPress={() => setExpanded(value => !value)} style={{ padding: 10 }}><Ionicons name={expanded ? "chevron-up" : "chevron-down"} size={21} color={colors.primary} /></Pressable></View>
    {expanded ? <View style={{ gap: 9 }}>
      <Pressable accessibilityRole="button" onPress={installWeb} style={{ backgroundColor: colors.primary, borderRadius: 13, padding: 13 }}><Text style={{ color: "white", fontWeight: "900", textAlign: "center" }}>{prompt ? "Install Shakti360 now" : "Show installation steps"}</Text></Pressable>
      {hasNativeRelease ? <View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap" }}>
        {androidUrl ? <Pressable accessibilityRole="link" onPress={() => Linking.openURL(androidUrl)} style={{ flex: 1, minWidth: 135, borderWidth: 1, borderColor: colors.border, borderRadius: 13, padding: 12 }}><Text style={{ color: colors.ink, fontWeight: "800", textAlign: "center" }}>Download Android APK</Text><Text style={{ color: colors.muted, fontSize: 11, textAlign: "center", marginTop: 3 }}>Signed native release</Text></Pressable> : null}
        {iosUrl ? <Pressable accessibilityRole="link" onPress={() => Linking.openURL(iosUrl)} style={{ flex: 1, minWidth: 135, borderWidth: 1, borderColor: colors.border, borderRadius: 13, padding: 12 }}><Text style={{ color: colors.ink, fontWeight: "800", textAlign: "center" }}>Open iPhone / iPad release</Text><Text style={{ color: colors.muted, fontSize: 11, textAlign: "center", marginTop: 3 }}>Signed App Store or TestFlight build</Text></Pressable> : null}
      </View> : null}
      {notice ? <Text accessibilityLiveRegion="polite" style={{ color: colors.primaryDark, fontSize: 12, lineHeight: 18 }}>{notice}</Text> : null}
    </View> : null}
  </View>;
}
