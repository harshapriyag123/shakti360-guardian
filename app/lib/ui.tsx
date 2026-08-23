import { useEffect, useState, type ReactElement, type ReactNode } from "react";
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, View, type RefreshControlProps, type TextInputProps } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { Link } from "expo-router";
import { useNetworkState } from "expo-network";

export const colors = {
  ink: "#13231D", muted: "#61716A", canvas: "#F4F7F4", card: "#FFFFFF",
  primary: "#126E52", primaryDark: "#0A4D3A", mint: "#DDF3E9", lime: "#DFF06D",
  coral: "#E86650", danger: "#B63D32", border: "#DDE6E1", gold: "#A46B06",
};

export function Screen({ children, refreshControl }: { children: ReactNode; refreshControl?: ReactElement<RefreshControlProps> }) {
  const network = useNetworkState();
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  const state = !mounted ? "ONLINE" : network.isConnected === false ? "OFFLINE" : network.isInternetReachable === false ? "LIMITED" : "ONLINE";
  return <SafeAreaView style={s.safe}><ScrollView refreshControl={refreshControl} contentContainerStyle={s.screen}><View style={s.safetyRail}><View accessibilityLabel={`Connection status ${state}`} style={s.networkPill}><View style={[s.networkDot, state !== "ONLINE" && { backgroundColor: colors.gold }]} /><Text style={s.networkText}>{state}</Text></View><Link href="/exit" asChild><Pressable accessibilityLabel="Quick exit to a neutral screen" style={s.exitButton}><Ionicons name="exit-outline" size={18} color={colors.muted} /><Text style={s.exitText}>Quick exit</Text></Pressable></Link><Link href="/sos" asChild><Pressable accessibilityLabel="Open SOS mode" style={s.sosButton}><Ionicons name="alert-circle" size={18} color="white" /><Text style={s.sosText}>SOS</Text></Pressable></Link></View>{children}</ScrollView></SafeAreaView>;
}

export function Eyebrow({ children }: { children: ReactNode }) { return <Text style={s.eyebrow}>{children}</Text>; }
export function Title({ children, subtitle }: { children: ReactNode; subtitle?: string }) {
  return <View style={{ gap: 7 }}><Text style={s.title}>{children}</Text>{subtitle ? <Text style={s.subtitle}>{subtitle}</Text> : null}</View>;
}
export function Card({ children, tone = "plain", style }: { children: ReactNode; tone?: "plain" | "mint" | "dark" | "danger"; style?: any }) {
  return <View style={[s.card, tone === "mint" && s.mint, tone === "dark" && s.dark, tone === "danger" && s.dangerCard, style]}>{children}</View>;
}
export function Action({ label, onPress, icon = "arrow-forward", variant = "primary", disabled = false }: { label: string; onPress: () => void; icon?: keyof typeof Ionicons.glyphMap; variant?: "primary" | "secondary" | "danger"; disabled?: boolean }) {
  return <Pressable disabled={disabled} onPress={onPress} style={({ pressed }) => [s.action, variant === "secondary" && s.secondary, variant === "danger" && s.danger, (pressed || disabled) && { opacity: .65 }]}><Text style={[s.actionText, variant === "secondary" && { color: colors.ink }]}>{label}</Text><Ionicons name={icon} size={19} color={variant === "secondary" ? colors.ink : "white"} /></Pressable>;
}
export function Field({ label, ...props }: TextInputProps & { label: string }) {
  return <View style={{ gap: 7 }}><Text style={s.label}>{label}</Text><TextInput placeholderTextColor="#87958F" {...props} style={[s.input, props.multiline && { minHeight: 124, textAlignVertical: "top" }, props.style]} /></View>;
}
export function PasswordField({ label, ...props }: Omit<TextInputProps, "secureTextEntry"> & { label: string }) {
  const [visible, setVisible] = useState(false);
  return <View style={{ gap: 7 }}><Text style={s.label}>{label}</Text><View style={{ position: "relative" }}><TextInput placeholderTextColor="#87958F" {...props} secureTextEntry={!visible} style={[s.input, { paddingRight: 56 }, props.style]} /><Pressable accessibilityRole="button" accessibilityLabel={`${visible ? "Hide" : "Show"} ${label.toLowerCase()}`} onPress={() => setVisible(value => !value)} style={{ position: "absolute", right: 5, top: 5, width: 44, height: 44, borderRadius: 12, alignItems: "center", justifyContent: "center" }}><Ionicons name={visible ? "eye-off-outline" : "eye-outline"} size={22} color={colors.primary} /></Pressable></View></View>;
}
export function Pill({ label, tone = "green" }: { label: string; tone?: "green" | "gold" | "red" | "gray" }) {
  const palette = tone === "red" ? ["#FCE6E2", colors.danger] : tone === "gold" ? ["#FFF2CF", colors.gold] : tone === "gray" ? ["#E9EFEC", colors.muted] : [colors.mint, colors.primary];
  return <View style={[s.pill, { backgroundColor: palette[0] }]}><Text style={[s.pillText, { color: palette[1] }]}>{label}</Text></View>;
}
export function Metric({ value, label }: { value: string | number; label: string }) { return <View style={s.metric}><Text style={s.metricValue}>{value}</Text><Text style={s.metricLabel}>{label}</Text></View>; }
export function Loading({ label = "Connecting securely…" }: { label?: string }) { return <View style={s.loading}><ActivityIndicator color={colors.primary} /><Text style={s.subtitle}>{label}</Text></View>; }
export function ErrorBanner({ message, retry }: { message: string; retry?: () => void }) { return <Card tone="danger"><Text style={s.errorTitle}>We couldn’t connect</Text><Text style={s.subtitle}>{message}</Text>{retry ? <Pressable onPress={retry}><Text style={s.retry}>Try again</Text></Pressable> : null}</Card>; }

export const s = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.canvas }, screen: { padding: 20, paddingBottom: 48, gap: 16, maxWidth: 760, width: "100%", alignSelf: "center" },
  eyebrow: { color: colors.primary, fontSize: 12, fontWeight: "800", letterSpacing: 1.4, textTransform: "uppercase" },
  title: { color: colors.ink, fontSize: 32, lineHeight: 38, fontWeight: "900", letterSpacing: -.8 }, subtitle: { color: colors.muted, fontSize: 15, lineHeight: 22 },
  card: { backgroundColor: colors.card, borderRadius: 22, padding: 18, gap: 11, borderWidth: 1, borderColor: colors.border, shadowColor: "#0B3527", shadowOpacity: .06, shadowRadius: 18, shadowOffset: { width: 0, height: 7 }, elevation: 2 },
  mint: { backgroundColor: colors.mint, borderColor: "#C4E7D8" }, dark: { backgroundColor: colors.primaryDark, borderColor: colors.primaryDark }, dangerCard: { backgroundColor: "#FFF4F1", borderColor: "#F2C8C0" },
  action: { minHeight: 54, borderRadius: 16, paddingHorizontal: 18, flexDirection: "row", justifyContent: "space-between", alignItems: "center", backgroundColor: colors.primary }, secondary: { backgroundColor: "white", borderWidth: 1, borderColor: colors.border }, danger: { backgroundColor: colors.danger }, actionText: { color: "white", fontWeight: "800", fontSize: 16 },
  label: { color: colors.ink, fontWeight: "700", fontSize: 14 }, input: { backgroundColor: "white", borderWidth: 1, borderColor: colors.border, borderRadius: 16, paddingHorizontal: 15, paddingVertical: 14, color: colors.ink, fontSize: 16 },
  pill: { alignSelf: "flex-start", borderRadius: 999, paddingHorizontal: 11, paddingVertical: 6 }, pillText: { fontWeight: "800", fontSize: 12, textTransform: "uppercase", letterSpacing: .5 },
  metric: { flex: 1, minWidth: 105, backgroundColor: "#F8FAF8", borderRadius: 16, padding: 14 }, metricValue: { color: colors.ink, fontSize: 26, fontWeight: "900" }, metricLabel: { color: colors.muted, fontSize: 12, lineHeight: 16, marginTop: 3 },
  loading: { flexDirection: "row", gap: 10, alignItems: "center", paddingVertical: 8 }, errorTitle: { color: colors.danger, fontWeight: "900", fontSize: 16 }, retry: { color: colors.danger, fontWeight: "800", marginTop: 4 },
  safetyRail: { flexDirection: "row", justifyContent: "flex-end", gap: 9, minHeight: 42 }, exitButton: { flexDirection: "row", gap: 6, alignItems: "center", paddingHorizontal: 12, borderRadius: 999, backgroundColor: "white", borderWidth: 1, borderColor: colors.border }, exitText: { color: colors.muted, fontWeight: "700", fontSize: 13 }, sosButton: { flexDirection: "row", gap: 6, alignItems: "center", paddingHorizontal: 15, borderRadius: 999, backgroundColor: colors.danger }, sosText: { color: "white", fontWeight: "900", fontSize: 13 },
  networkPill: { marginRight: "auto", flexDirection: "row", gap: 6, alignItems: "center" }, networkDot: { width: 8, height: 8, borderRadius: 4, backgroundColor: colors.primary }, networkText: { color: colors.muted, fontWeight: "800", fontSize: 10 },
});
