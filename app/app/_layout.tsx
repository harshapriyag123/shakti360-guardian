import { Tabs } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { Ionicons } from "@expo/vector-icons";
import { Image, Text, View } from "react-native";
import { colors } from "../lib/ui";
import { AppErrorBoundary } from "../lib/ErrorBoundary";

const icons: Record<string, keyof typeof Ionicons.glyphMap> = { index: "home", journey: "navigate", resources: "map", guardians: "people", toolkit: "grid" };
const titles: Record<string, string> = { journey: "Journey", resources: "Nearby help", guardians: "Guardian Circle", toolkit: "Safety toolkit", cyber: "Scam scanner", evidence: "Evidence vault", impact: "Impact", patterns: "Pattern insights", privacy: "Privacy check", receipts: "Privacy receipts", readiness: "Safety readiness", sos: "SOS", profile: "My account", explore: "Explore", register: "Create account", login: "Sign in", "guardian-invite": "Guardian invitation" };
function BrandHeader({ title }: { title: string }) {
  return <View accessibilityRole="header" style={{ flexDirection: "row", alignItems: "center", gap: 10 }}><Image source={require("../public/shakti360-icon.png")} accessibilityLabel="Shakti360 Guardian logo" style={{ width: 34, height: 34, borderRadius: 10 }} resizeMode="cover" /><View><Text style={{ color: colors.primary, fontSize: 10, lineHeight: 12, fontWeight: "900", letterSpacing: 1 }}>SHAKTI360</Text><Text numberOfLines={1} style={{ color: colors.ink, fontSize: 16, lineHeight: 19, fontWeight: "900", maxWidth: 210 }}>{title}</Text></View></View>;
}
export default function Layout() {
  return <AppErrorBoundary><StatusBar style="dark" /><Tabs screenOptions={({ route }) => ({ headerTitle: () => <BrandHeader title={titles[route.name] || "Shakti360 Guardian"} />, headerTitleAlign: "center", headerShadowVisible: false, headerStyle: { backgroundColor: colors.canvas }, headerTintColor: colors.ink, tabBarActiveTintColor: colors.primary, tabBarInactiveTintColor: colors.muted, tabBarLabelStyle: { fontSize: 11, fontWeight: "700" }, tabBarStyle: { height: 66, paddingTop: 7, paddingBottom: 8, borderTopColor: colors.border, backgroundColor: "white" }, tabBarIcon: ({ color, size }) => <Ionicons name={icons[route.name] || "ellipse"} color={color} size={size} /> })}>
    <Tabs.Screen name="index" options={{ title: "Home", headerShown: false }} />
    <Tabs.Screen name="journey" options={{ title: "Journey" }} />
    <Tabs.Screen name="resources" options={{ title: "Map" }} />
    <Tabs.Screen name="guardians" options={{ title: "Guardians" }} />
    <Tabs.Screen name="toolkit" options={{ title: "Toolkit" }} />
    {['cyber','evidence','impact','patterns','privacy','receipts','readiness','sos','exit','fake-call','judge','register','login','profile','explore','guardian-invite'].map(name => <Tabs.Screen key={name} name={name} options={{ href: null }} />)}
  </Tabs></AppErrorBoundary>;
}
