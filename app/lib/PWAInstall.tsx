import { useEffect, useState } from "react";
import { Linking, Platform, Pressable, Text, View } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "./ui";

type InstallPrompt = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

type ClientInfo = {
  device: "ios" | "android" | "desktop";
  browser: "chrome" | "edge" | "firefox" | "safari" | "samsung" | "other";
  deviceLabel: string;
};

const defaultClient: ClientInfo = { device: "desktop", browser: "other", deviceLabel: "computer" };

function detectClient(): ClientInfo {
  if (typeof navigator === "undefined") return defaultClient;
  const userAgent = navigator.userAgent.toLowerCase();
  const ipadDesktopMode = navigator.platform === "MacIntel" && navigator.maxTouchPoints > 1;
  const device = /iphone|ipad|ipod/.test(userAgent) || ipadDesktopMode
    ? "ios"
    : /android/.test(userAgent)
      ? "android"
      : "desktop";

  let browser: ClientInfo["browser"] = "other";
  if (/samsungbrowser/.test(userAgent)) browser = "samsung";
  else if (/edgios|edga|edg\//.test(userAgent)) browser = "edge";
  else if (/fxios|firefox/.test(userAgent)) browser = "firefox";
  else if (/crios|chrome/.test(userAgent)) browser = "chrome";
  else if (/safari/.test(userAgent)) browser = "safari";

  return {
    device,
    browser,
    deviceLabel: device === "ios" ? "iPhone or iPad" : device === "android" ? "Android device" : "computer",
  };
}

function isStandalone() {
  if (typeof window === "undefined" || typeof navigator === "undefined") return false;
  const iosNavigator = navigator as Navigator & { standalone?: boolean };
  return iosNavigator.standalone === true || window.matchMedia("(display-mode: standalone)").matches;
}

function installationSteps(client: ClientInfo) {
  if (client.device === "ios") {
    if (client.browser === "safari") {
      return "In Safari, tap the Share button (the square with an up arrow), choose Add to Home Screen, then tap Add.";
    }
    return "Open the browser Share menu and choose Add to Home Screen. If that option is missing, open this page in Safari and use Share → Add to Home Screen.";
  }
  if (client.device === "android") {
    if (client.browser === "samsung") {
      return "In Samsung Internet, open the menu, choose Add page to, then choose Home screen.";
    }
    if (client.browser === "firefox") {
      return "In Firefox, open the menu and choose Install. If Install is unavailable, open this page in Chrome.";
    }
    return "Open the browser menu (⋮), choose Install app or Add to Home screen, then confirm.";
  }
  if (client.browser === "safari") {
    return "In Safari on macOS, open the File menu and choose Add to Dock. If the option is unavailable, update macOS or use Chrome or Edge.";
  }
  if (client.browser === "firefox") {
    return "Firefox desktop does not offer full PWA installation. Open this page in Chrome or Edge, then use the install icon in the address bar.";
  }
  return "In Chrome or Edge, select the install icon in the address bar. You can also open the browser menu and choose Install Shakti360.";
}

export function PWAInstall() {
  const [client, setClient] = useState<ClientInfo>(defaultClient);
  const [deferredPrompt, setDeferredPrompt] = useState<InstallPrompt | null>(null);
  const [installed, setInstalled] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [notice, setNotice] = useState("");
  const androidUrl = process.env.EXPO_PUBLIC_ANDROID_DOWNLOAD_URL;
  const iosUrl = process.env.EXPO_PUBLIC_IOS_DOWNLOAD_URL;
  const hasNativeRelease = Boolean(androidUrl || iosUrl);

  useEffect(() => {
    if (Platform.OS !== "web" || typeof window === "undefined") return;
    setClient(detectClient());

    const displayMode = window.matchMedia("(display-mode: standalone)");
    const syncInstalled = () => setInstalled(isStandalone());
    const capture: EventListener = event => {
      event.preventDefault();
      setDeferredPrompt(event as InstallPrompt);
    };
    const complete = () => {
      setInstalled(true);
      setDeferredPrompt(null);
    };

    syncInstalled();
    if (typeof displayMode.addEventListener === "function") displayMode.addEventListener("change", syncInstalled);
    else displayMode.addListener(syncInstalled);
    window.addEventListener("beforeinstallprompt", capture);
    window.addEventListener("appinstalled", complete);

    return () => {
      if (typeof displayMode.removeEventListener === "function") displayMode.removeEventListener("change", syncInstalled);
      else displayMode.removeListener(syncInstalled);
      window.removeEventListener("beforeinstallprompt", capture);
      window.removeEventListener("appinstalled", complete);
    };
  }, []);

  if (Platform.OS !== "web" || installed) return null;

  async function installWeb() {
    setExpanded(true);
    setNotice("");
    if (!deferredPrompt) {
      setNotice(installationSteps(client));
      return;
    }

    const currentPrompt = deferredPrompt;
    setDeferredPrompt(null);
    try {
      await currentPrompt.prompt();
      const choice = await currentPrompt.userChoice;
      setNotice(choice.outcome === "accepted"
        ? "Installation accepted. Shakti360 will appear with your other apps."
        : "Installation was cancelled. " + installationSteps(client));
    } catch {
      setNotice("The browser could not open its install dialog. " + installationSteps(client));
    }
  }

  async function openRelease(url: string, label: string) {
    try {
      await Linking.openURL(url);
    } catch {
      setExpanded(true);
      setNotice(label + " could not be opened on this device. You can still install the web app using the steps above.");
    }
  }

  const actionLabel = deferredPrompt
    ? "Install Shakti360 now"
    : client.device === "ios"
      ? "Add to Home Screen"
      : client.device === "android"
        ? "Install on Android"
        : "Install on this computer";

  return <View style={{ borderWidth: 1, borderColor: colors.border, borderRadius: 18, padding: 14, backgroundColor: "white", gap: 12 }}>
    <View style={{ flexDirection: "row", alignItems: "center", gap: 12 }}>
      <View style={{ width: 44, height: 44, borderRadius: 14, backgroundColor: colors.mint, alignItems: "center", justifyContent: "center" }}>
        <Ionicons name="download-outline" size={25} color={colors.primary} />
      </View>
      <View style={{ flex: 1 }}>
        <Text style={{ color: colors.ink, fontWeight: "900", fontSize: 16 }}>Install Shakti360</Text>
        <Text style={{ color: colors.muted, fontSize: 13, lineHeight: 18, marginTop: 2 }}>Add the secure web app to this {client.deviceLabel}—no app store required.</Text>
      </View>
    </View>

    <Pressable
      accessibilityRole="button"
      accessibilityLabel={actionLabel}
      accessibilityHint={"Installs Shakti360 or shows the correct steps for this " + client.deviceLabel}
      accessibilityState={{ expanded }}
      onPress={installWeb}
      style={({ pressed }) => ({ minHeight: 50, backgroundColor: colors.primary, borderRadius: 14, paddingHorizontal: 16, flexDirection: "row", alignItems: "center", justifyContent: "space-between", opacity: pressed ? 0.78 : 1 })}
    >
      <Text style={{ color: "white", fontWeight: "900", fontSize: 15 }}>{actionLabel}</Text>
      <Ionicons name={deferredPrompt ? "download" : "arrow-forward"} size={20} color="white" />
    </Pressable>

    {expanded ? <View style={{ gap: 9 }}>
      {notice ? <View style={{ backgroundColor: colors.mint, borderRadius: 13, padding: 12 }}>
        <Text accessibilityLiveRegion="polite" style={{ color: colors.primaryDark, fontSize: 13, lineHeight: 19, fontWeight: "700" }}>{notice}</Text>
      </View> : null}
      <Pressable accessibilityRole="button" onPress={() => setExpanded(false)} style={{ minHeight: 44, justifyContent: "center", alignItems: "center" }}>
        <Text style={{ color: colors.primary, fontWeight: "800" }}>Hide installation help</Text>
      </Pressable>
    </View> : null}

    {hasNativeRelease ? <View style={{ flexDirection: "row", gap: 8, flexWrap: "wrap" }}>
      {androidUrl ? <Pressable accessibilityRole="link" onPress={() => openRelease(androidUrl, "The Android release")} style={{ flex: 1, minWidth: 150, borderWidth: 1, borderColor: colors.border, borderRadius: 13, padding: 12 }}>
        <Text style={{ color: colors.ink, fontWeight: "800", textAlign: "center" }}>Download Android app</Text>
        <Text style={{ color: colors.muted, fontSize: 11, textAlign: "center", marginTop: 3 }}>Signed release</Text>
      </Pressable> : null}
      {iosUrl ? <Pressable accessibilityRole="link" onPress={() => openRelease(iosUrl, "The iPhone and iPad release")} style={{ flex: 1, minWidth: 150, borderWidth: 1, borderColor: colors.border, borderRadius: 13, padding: 12 }}>
        <Text style={{ color: colors.ink, fontWeight: "800", textAlign: "center" }}>Open iPhone / iPad app</Text>
        <Text style={{ color: colors.muted, fontSize: 11, textAlign: "center", marginTop: 3 }}>App Store or TestFlight</Text>
      </Pressable> : null}
    </View> : null}
  </View>;
}
